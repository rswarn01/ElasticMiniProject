from elastic.constants import SNOWFLAKE_VIEW_NAME
from elastic.extensions import azure
from flask import current_app as app
from elastic.models import Action, Role
from elastic.utils.serializers import EmailData
from elastic.models import User, Notification
from elastic.utils.sendgrid_mail import send_email


def get_attachments_from_azure(path):
    attachment = azure.download(path)
    content = attachment.readall()
    return content


def assign_notification(
    usage_tracking, target_user_id, file_name=None, action_name=None,
):
    """Create notification record"""

    _app_env = app.config["APP_ENV"]
    sme_id = None
    list_of_email = list()
    list_of_admin_email = list()
    list_of_sme_email = list()
    admin_body = ""
    admin_subject = ""
    user_body = ""
    user_subject = ""
    sme_body = ""
    sme_subject = ""
    requestor_id = usage_tracking.user.user_id
    if action_name is None:
        action_name = usage_tracking.action.action_name
    if usage_tracking.query_input:
        client_name = usage_tracking.query_input.get("client_name", None)
        sme_id = usage_tracking.query_input.get("sme_id", None)
        admin_name = usage_tracking.query_input.get("admin_name", None)
        user_id = usage_tracking.query_input.get("user_id", None)
    username = usage_tracking.full_username
    bell_notification = None

    if action_name == Action.ACTION_CLIENT_REQUEST:
        bell_notification = f"{username} has requested to add {client_name}"
        admin_body = f"""
            Hi,
            <br>
            {username} has requested for access to upload data to the elasticmarking application.
            <br>
            Please approve.
            """
        admin_subject = str(_app_env) + " - " + "New client request"

    if action_name == Action.ACTION_CLIENT_LINK:
        bell_notification = f"{username} has approved your request to add client {client_name} on elasticmarking app"
        user_body = """
            Hi,
            <br>
            Request for uploading data to the elasticmarking application has been approved.
            """
        user_subject = str(_app_env) + " - " + "Request approved"

    if action_name == Action.ACTION_RAW_FILE_UPLOADED:
        bell_notification = (
            f'{username} has uploaded raw file "{file_name}" for client {client_name}'
        )
        admin_body = f"""
            Hi,
            <br>
            {username} has uploaded raw data to the elasticmarking application.
            <br>
            Please approve.
            """
        admin_subject = str(_app_env) + " - " + "Raw File Received"

    if action_name == Action.ACTION_ASSIGN_SME_FOR_REVIEW:
        bell_notification = f'{username} has requested you to review "{file_name}"'
        sme_body = f"""
            Hi,
            <br>
            {username} has requested for review of the normalized data on elasticmarking application.
            <br>
            Please review
            """
        sme_subject = str(_app_env) + " - " + "Review request"

    if action_name == Action.ACTION_ADMIN_CREATE:
        admin_body = f"""
            Hi,
            <br>
            {username} has added another {admin_name} as Admin on elasticmarking Application.
            """
        admin_subject = str(_app_env) + " - " + "New administrator added"

    if action_name == Action.ACTION_REVIEW_REJECTED:
        bell_notification = (
            f'{username} has rejected to review your normalized file: "{file_name}"'
        )
        user_body = f"""
            Hi,
            <br>
            {username} has rejected to review your normalized file:
            <br>
            {file_name}
            """
        user_subject = str(_app_env) + " - " + "Review Rejected"

    if action_name == Action.ACTION_REVIEW_ACCEPTED:
        bell_notification = (
            f'{username} has accepted to review your normalized file: "{file_name}"'
        )
        user_body = f"""
            Hi,
            <br>
            {username} has approved to review your normalized file:
            <br>
            {file_name}
            """
        user_subject = str(_app_env) + " - " + "Review approved"

    if action_name == Action.ACTION_FILE_ACCEPTED:
        bell_notification = (
            f'{username} has approved your normalized file: "{file_name}"'
        )
        user_body = f"""
            Hi,
            <br>
            {username} has approved your normalized file:
            <br>
            {file_name}
            """
        user_subject = str(_app_env) + " - " + "File approved"

    if action_name == Action.ACTION_FILE_REJECTED:
        bell_notification = (
            f'{username} has rejected your normalized file: "{file_name}"'
        )
        user_body = f"""
            Hi,
            <br>
            {username} has rejected your normalized file:
            <br>
            {file_name}
            """
        user_subject = str(_app_env) + " - " + "File rejected"

    if action_name == Action.ACTION_FILE_DISABLE:
        bell_notification = (
            f'{username} has marked your file "{file_name}" as duplicate.'
        )
        Notification.create_notification(
            notification_message=bell_notification,
            user_id=target_user_id,
            usage_tracking_id=usage_tracking.usage_tracking_id,
            scheduled_notification_status=True,
        )

    if len(user_body) > 0:
        if bell_notification is not None:
            notification = Notification.create_notification(
                notification_message=bell_notification,
                user_id=target_user_id,
                usage_tracking_id=usage_tracking.usage_tracking_id,
                scheduled_notification_status=True,
            )
            user_email = EmailData(
                [notification.user.email_address],
                user_subject,
                user_subject,
                user_body,
                file_name,
            )
            list_of_email.append(user_email.__dict__)

    if len(admin_body) > 0:
        admin_ids = User.get_user_by_rolename(rolename=User.ROLE_ADMIN)
        for admin_id in admin_ids:
            if admin_id != requestor_id and admin_id != user_id:
                notification = Notification.create_notification(
                    bell_notification,
                    admin_id,
                    usage_tracking.usage_tracking_id,
                    scheduled_notification_status=True,
                )
                list_of_admin_email.append(notification.user.email_address)

        if len(list_of_admin_email) > 0:
            admin_email = EmailData(
                list_of_admin_email,
                admin_subject,
                admin_subject,
                admin_body,
                file_name,
            )
            list_of_email.append(admin_email.__dict__)

    if len(sme_body) > 0:
        if sme_id is None:
            sme_ids = User.get_user_by_rolename(rolename=User.ROLE_SME)
        else:
            sme_objects = User.query.filter(User.user_id == sme_id).all()
            sme_ids = [x.user_id for x in sme_objects]
        for sme_id in sme_ids:
            if sme_id != requestor_id:
                notification = Notification.create_notification(
                    notification_message=bell_notification,
                    user_id=sme_id,
                    usage_tracking_id=usage_tracking.usage_tracking_id,
                    scheduled_notification_status=True,
                )
                list_of_sme_email.append(notification.user.email_address)

            if len(list_of_sme_email) > 0:
                sme_email = EmailData(
                    list_of_sme_email, sme_subject, sme_subject, sme_body, file_name,
                )
                list_of_email.append(sme_email.__dict__)

    print(list_of_email)
    for email in list_of_email:
        send_email(
            email=email["email"],
            email_template="email_notification",
            title=email["title"],
            data=email,
            subject=email["subject"],
        )


def send_privacy_agreement(user_email):
    list_of_email = []
    body = None
    subject = f"Privacy Agreement"

    email_data = EmailData([user_email], subject, subject, body,)

    list_of_email.append(email_data.__dict__)

    print(list_of_email)
    for email in list_of_email:
        send_email(
            email=email["email"],
            email_template="privacy_agreement",
            title=email["title"],
            data=email,
            subject=email["subject"],
        )

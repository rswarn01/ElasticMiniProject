import logging
import os
import time
from elastic.extensions import db
from flask import render_template
from flask_praetorian import current_user_id, current_user
from elastic.models import FileDetail, Action, UsageTracking, User, Role
from azure.core.exceptions import AzureError
from elastic.extensions import azure
from elastic.utils import Response
import base64
from sendgrid import SendGridAPIClient
from elastic.constants import (
    AZURE_BASE_PATH_ATTACHMENTS,
    CREATE_ADMIN_SUBJECT,
    REMOVE_ADMIN_SUBJECT,
)
from flask import current_app as app
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
    Content,
)


def send_mail(
    from_email: str,
    to_emails: list,
    email_template: str,
    subject: str = None,
    data: dict = None,
    input_sheet=None,
):

    data["app_url"] = app.config["APP_BASE_URL"]
    _img_path = "/Kearney_Logo.png"
    data["kearney_logo"] = str(app.config.get("APP_BASE_URL")) + _img_path

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=Content("text/html", render_template(email_template, data=data)),
    )

    """Attaching file uploaded by user from Frontend."""
    if input_sheet is not None:
        buf = input_sheet.read()
        encoded = base64.b64encode(buf).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType(input_sheet.content_type)
        attachment.file_name = FileName(input_sheet.filename)
        attachment.disposition = Disposition("attachment")
        message.attachment = attachment

    try:
        sendgrid_client = SendGridAPIClient(api_key=app.config["MAIL_SENDGRID_API_KEY"])
        sendgrid_client.send(message)

    except Exception as e:
        logging.error(str(e))

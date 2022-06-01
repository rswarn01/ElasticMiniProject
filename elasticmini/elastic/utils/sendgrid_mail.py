import logging
from flask_mail import Message
from flask import render_template
from elastic.extensions import mail
from flask import current_app as app
from threading import Thread
from sendgrid.helpers.mail import Mail
from flask_mail import Message


def _send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
        logging.info("Email sent to {email}".format(email=msg.recipients))


def send_email(
    email: list,
    email_template: str,
    sender: str = None,
    title: str = None,
    subject: str = None,
    data: dict = None,
):
    app_object = app._get_current_object()
    data["app_url"] = app.config["APP_BASE_URL"]
    _img_path = "/Kearney_Logo.png"
    data["kearney_logo"] = str(app.config.get("APP_BASE_URL")) + _img_path
    if sender:
        msg = Message(
            subject=subject, sender=app.config["MAIL_DEFAULT_SENDER"], recipients=email
        )
    else:
        msg = Message(subject=subject, recipients=email)
    # Adding template of mail
    msg.html = render_template(email_template + ".html", title=title, data=data)
    Thread(target=_send_async_email, args=(app_object, msg)).start()

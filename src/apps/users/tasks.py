import json
import os
import subprocess

from celery import shared_task, states
from celery.exceptions import Ignore
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


# @shared_task(bind=True)
def send_email(to: str | list[str], email_type: str, email_data: dict):
    print("AT Task")
    print(email_type)
    print(email_data)

    if email_type == "ACCOUNT_ACTIVATION":
        rendered_email = {
            "html": render_to_string(
                "users/emails/account_activation.html", 
                context=email_data
            ),
            "subject": "Account Activation"
        }

    print(rendered_email)
    email = EmailMessage(
        rendered_email['subject'],
        rendered_email['html'],
        settings.EMAIL_FROM_ADDRESS,
        to,
        reply_to=settings.EMAIL_REPLY_ADDRESS,
    )
    email.content_subtype = 'html'
    return {'sent_emails_count': email.send()}
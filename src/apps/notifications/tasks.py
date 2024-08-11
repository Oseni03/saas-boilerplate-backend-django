from celery import shared_task
from django.conf import settings

import requests
from twilio.rest import Client


@shared_task(bind=True)
def send_sms_notification(self, phone_number, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.message.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )


@shared_task(bind=True)
def send_push_notification(self, device_token, type, message):
    # Example for Firebase Cloud Messaging (FCM)
    headers = {
        "Authorization": f"key={settings.FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": device_token,
        "notification": {
            "title": f"{type} Notification",
            "body": message,
        }
    }
    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, json=payload)
    return response
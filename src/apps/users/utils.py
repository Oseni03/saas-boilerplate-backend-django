from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


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


def set_auth_cookie(response, data):
    cookie_max_age = settings.COOKIE_MAX_AGE
    access = data.get(settings.ACCESS_TOKEN_COOKIE)
    refresh = data.get(settings.REFRESH_TOKEN_COOKIE)
    response.set_cookie(settings.ACCESS_TOKEN_COOKIE, access, max_age=cookie_max_age, httponly=True)

    if refresh:
        response.set_cookie(
            settings.REFRESH_TOKEN_COOKIE,
            refresh,
            max_age=cookie_max_age,
            httponly=True,
            path=reverse("jwt_token_refresh"),
        )

        response.set_cookie(
            settings.REFRESH_TOKEN_LOGOUT_COOKIE,
            refresh,
            max_age=cookie_max_age,
            httponly=True,
            path=reverse("logout"),
        )


def reset_auth_cookie(response):
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE)
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE)
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE, path=reverse("jwt_token_refresh"))
    response.delete_cookie(settings.REFRESH_TOKEN_LOGOUT_COOKIE, path=reverse("logout"))


def generate_otp_auth_token(user):
    otp_auth_token = AccessToken()
    otp_auth_token["user_id"] = str(user.id)
    otp_auth_token.set_exp(from_time=timezone.now(), lifetime=settings.OTP_AUTH_TOKEN_LIFETIME_MINUTES)

    return otp_auth_token

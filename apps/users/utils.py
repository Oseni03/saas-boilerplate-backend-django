from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings


def set_auth_cookie(response, data):
    cookie_max_age = settings.AUTH_COOKIE_MAX_AGE
    httponly = settings.AUTH_COOKIE_HTTP_ONLY
    secure=settings.AUTH_COOKIE_SECURE,
    samesite=settings.AUTH_COOKIE_SAMESITE
    access = data.get(settings.AUTH_ACCESS_COOKIE)
    refresh = data.get(settings.AUTH_REFRESH_COOKIE)
    otp_auth_token = data.get(settings.OTP_AUTH_TOKEN_COOKIE)
    
    response.set_cookie(
        settings.AUTH_ACCESS_COOKIE, 
        access, 
        max_age=cookie_max_age, 
        path=settings.AUTH_COOKIE_PATH,
        httponly=True,
        secure=secure,
        samesite=samesite,
    )

    if refresh:
        response.set_cookie(
            settings.AUTH_REFRESH_COOKIE,
            refresh,
            max_age=cookie_max_age,
            httponly=httponly,
            path=settings.AUTH_REFRESH_PATH,
            secure=secure,
            samesite=samesite,
        )

        response.set_cookie(
            settings.AUTH_REFRESH_LOGOUT_COOKIE,
            refresh,
            max_age=cookie_max_age,
            httponly=httponly,
            path=settings.AUTH_REFRESH_LOGOUT_PATH,
            secure=secure,
            samesite=samesite,
        )
    elif otp_auth_token:
        response.set_cookie(
            settings.OTP_AUTH_TOKEN_COOKIE, 
            otp_auth_token, 
            max_age=cookie_max_age, 
            path=settings.AUTH_COOKIE_PATH,
            httponly=True,
            secure=secure,
            samesite=samesite,
        )


def reset_auth_cookie(response):
    response.delete_cookie(
        settings.AUTH_ACCESS_COOKIE,
        path=settings.AUTH_COOKIE_PATH,
    )
    response.delete_cookie(settings.AUTH_REFRESH_COOKIE)
    response.delete_cookie(
        settings.AUTH_REFRESH_COOKIE, 
    )
    response.delete_cookie(
        settings.AUTH_REFRESH_LOGOUT_COOKIE, 
    )
    response.delete_cookie(
        settings.OTP_AUTH_TOKEN_COOKIE, 
    )


def generate_otp_auth_token(user):
    otp_auth_token = AccessToken()
    otp_auth_token["user_id"] = str(user.id)
    otp_auth_token.set_exp(from_time=timezone.now(), lifetime=settings.OTP_AUTH_TOKEN_LIFETIME_MINUTES)

    return otp_auth_token

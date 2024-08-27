"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
import json
from django.urls import reverse_lazy
import environ
import datetime
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DJANGO_DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR, '.venv'))

ASGI_APPLICATION = "core.asgi.application"

ENVIRONMENT_NAME = env("ENVIRONMENT_NAME", default="")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-fl8wx8v^f+napyno=zf#)et=+4n7-uyovd+&n**jhf!bgd8z!)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DJANGO_DEBUG")
IS_LOCAL_DEBUG = DEBUG and ENVIRONMENT_NAME == "local"
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# Application definition

DJANGO_CORE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_extensions",
    "drf_yasg",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "social_django",
    "whitenoise",
    'channels',
    "django_filters",
]

LOCAL_APPS = [
    "apps.users",
    "apps.notifications",
    "apps.feedbacks",
    "apps.subscriptions",
    "apps.customers",
]

INSTALLED_APPS = (
    [
        "daphne",
    ]
    + DJANGO_CORE_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
)

SILENCED_SYSTEM_CHECKS = []

MIDDLEWARE = [
    "common.middleware.ManageCookiesMiddleware",
    "common.middleware.SetAuthTokenCookieMiddleware",
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    # "common.middleware.UserProfileMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

PASSWORD_HASHERS = env.list(
    "DJANGO_PASSWORD_HASHERS",
    default=[
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ],
)

WSGI_APPLICATION = "core.wsgi.application"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env('DJANGO_LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        '*': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DB_CONNECTION = json.loads(env("DB_CONNECTION"))
DB_PROXY_ENDPOINT = env("DB_PROXY_ENDPOINT", default=None)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_CONNECTION["dbname"],
        "USER": DB_CONNECTION["username"],
        "PASSWORD": DB_CONNECTION["password"],
        "HOST": DB_PROXY_ENDPOINT or DB_CONNECTION["host"],
        "PORT": DB_CONNECTION["port"],
    },
    "channels_postgres": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_CONNECTION["dbname"],
        "USER": DB_CONNECTION["username"],
        "PASSWORD": DB_CONNECTION["password"],
        "HOST": DB_PROXY_ENDPOINT or DB_CONNECTION["host"],
        "PORT": DB_CONNECTION["port"],
    },
}

REDIS_CONNECTION = env("REDIS_CONNECTION")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{"address": REDIS_CONNECTION}],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CONNECTION,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Storages
# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-STORAGES
STORAGES = {
    "default": {
        "BACKEND": "common.storages.CustomS3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

LOCALE_PATHS = []

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "common.utils.custom_exception_handler",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'apps.users.authentication.CustomJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day"},
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=env.int('ACCESS_TOKEN_LIFETIME_MINUTES', default=60)),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=env.int('REFRESH_TOKEN_LIFETIME_DAYS', default=7)),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
AUTH_ACCESS_COOKIE = 'access'
AUTH_REFRESH_COOKIE = 'refresh'
AUTH_REFRESH_PATH = reverse_lazy("jwt_token_refresh")
AUTH_REFRESH_LOGOUT_COOKIE = 'refresh_logout'
AUTH_REFRESH_LOGOUT_PATH = reverse_lazy("logout")
AUTH_COOKIE_MAX_AGE = 3600 * 24 * 14  # 14 days
AUTH_COOKIE_SECURE = env('AUTH_COOKIE_SECURE', default='True')
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_PATH = '/'
AUTH_COOKIE_SAMESITE = 'None'

SOCIAL_AUTH_USER_MODEL = "users.User"
SOCIAL_AUTH_USER_FIELDS = ['email', 'username']
SOCIAL_AUTH_STRATEGY = "apps.users.strategy.DjangoJWTStrategy"
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_REDIRECT_IS_HTTPS = env.bool('SOCIAL_AUTH_REDIRECT_IS_HTTPS', default=True)
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS = env.list('SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS', default=[])
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', default='')
SOCIAL_AUTH_FACEBOOK_KEY = env('SOCIAL_AUTH_FACEBOOK_KEY', default='')
SOCIAL_AUTH_FACEBOOK_SECRET = env('SOCIAL_AUTH_FACEBOOK_SECRET', default='')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'public_profile']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email',
}
SOCIAL_AUTH_LOGIN_ERROR_URL = "/"
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ["locale"]

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'config.urls_api.api_info',
    "SECURITY_DEFINITIONS": {"api_key": {"type": "apiKey", "in": "header", "name": "Authorization"}},
}

HASHID_FIELD_SALT = env("HASHID_FIELD_SALT")

USER_NOTIFICATION_IMPL = "config.notifications.stdout"

STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="sk_test_<CHANGE_ME>")
STRIPE_LIVE_MODE = env.bool("STRIPE_LIVE_MODE", default=False)
STRIPE_ENABLED = env("STRIPE_ENABLED", default=False)
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")

SUBSCRIPTION_TRIAL_PERIOD_DAYS = env("SUBSCRIPTION_TRIAL_PERIOD_DAYS", default=7)

NOTIFICATIONS_STRATEGIES = ["InAppNotificationStrategy", "EmailNotificationStrategy", "SMSNotificationStrategy", "PushNotificationStrategy"]

WEB_SOCKET_API_ENDPOINT_URL = env("WEB_SOCKET_API_ENDPOINT_URL", default="")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", default=[])
RATELIMIT_IP_META_KEY = "common.utils.get_client_ip"

OTP_AUTH_ISSUER_NAME = env("OTP_AUTH_ISSUER_NAME", default="")
OTP_AUTH_TOKEN_COOKIE = 'otp_auth_token'
OTP_AUTH_TOKEN_LIFETIME_MINUTES = datetime.timedelta(minutes=env.int('OTP_AUTH_TOKEN_LIFETIME_MINUTES', default=5))
OTP_VALIDATE_PATH = "/auth/validate-otp"

OPENAI_API_KEY = env("OPENAI_API_KEY", default="")

UPLOADED_DOCUMENT_SIZE_LIMIT = env.int("UPLOADED_DOCUMENT_SIZE_LIMIT", default=10 * 1024 * 1024)
USER_DOCUMENTS_NUMBER_LIMIT = env.int("USER_DOCUMENTS_NUMBER_LIMIT", default=10)

REDIS_CONNECTION = f'{env("REDIS_CONNECTION")}/0'

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django_ses.SESBackend")
EMAIL_HOST = env("EMAIL_HOST", default=None)
EMAIL_PORT = env("EMAIL_PORT", default=None)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default=None)
EMAIL_FROM_ADDRESS = env("EMAIL_FROM_ADDRESS", default=None)
EMAIL_REPLY_ADDRESS = env.list("EMAIL_REPLY_ADDRESS", default=(EMAIL_FROM_ADDRESS,))

TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_PHONE_NUMBER = env("TWILIO_PHONE_NUMBER", default="")
FCM_SERVER_KEY = env("FCM_SERVER_KEY", default="")

# USER SUBSCRIPTION SETTINGS
ALLOW_CUSTOM_GROUP = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True

CHECKOUT_SUCCESS_URL = "http://localhost:3000/dashboard"
CHECKOUT_CANCEL_URL = "http://localhost:3000/pricing"
CUSTOMER_PORTAL_SESSION_RETURN_URL = "http://localhost:3000/dashboard"
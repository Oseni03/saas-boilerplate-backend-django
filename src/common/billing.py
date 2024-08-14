import stripe
from django.conf import settings

DJANGO_DEBUG = settings.DEBUG
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY

if "sk_test" in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("Inavlid stripe key for production")

stripe.api_key = STRIPE_SECRET_KEY


def create_customer(email, raw=False):
    response = stripe.Customer.create(
        email=email
    )
    if raw:
        return response
    return response.id # stripe_id
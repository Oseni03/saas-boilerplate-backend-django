import stripe
from django.conf import settings

DJANGO_DEBUG = settings.DEBUG
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY

if "sk_test" in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("Inavlid stripe key for production")

stripe.api_key = STRIPE_SECRET_KEY


def create_customer(email: str, metadata: dict, raw=False):
    response = stripe.Customer.create(
        email=email, 
        metadata=metadata,
    )
    if raw:
        return response
    return response.id # stripe_id


def create_product(name: str, metadata: dict, raw=False):
    response = stripe.Product.create(
        name=name, 
        metadata=metadata,
    )
    if raw:
        return response
    return response.id # stripe_id


def create_price(
        currency: str, 
        unit_amount: int, 
        interval: str, 
        trial_period_days,
        product: str, 
        metadata: dict, 
        raw=False
    ): 
    response = stripe.Price.create(
        currency=currency, 
        unit_amount=unit_amount, 
        recurring={
            "interval": interval,
            "trial_period_days": trial_period_days,
        }, 
        product=product,
        metadata=metadata,
    )
    if raw:
        return response
    return response.id # stripe_id
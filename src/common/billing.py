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


def create_subscription(customer_id: str, price_id: str, raw=False):
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{
            "price": price_id,
        }],
        payment_behavior="default_incomplete",
        payment_settings={"save_default_payment_method": "on_subscription"},
        expand=["latest_invoice.payment_intent"],
    )
    response = {
        "subscription_id": subscription.id, 
        "client_secret": subscription.latest_invoice.payment_intent.client_secret,
    }
    if raw:
        return subscription
    return response


def update_subscription(subscription_id: str, new_price_id: str, raw=False):
    subscription = stripe.Subscription.retrieve(subscription_id)

    response = stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=False,
        items=[{
            "id": subscription["items"]["data"][0].id,
            "price": new_price_id,
        }]
    )
    if raw:
        return response
    return response.id
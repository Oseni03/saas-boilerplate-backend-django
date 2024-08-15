import stripe
from django.conf import settings

from apps.subscriptions import utils

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


def create_subscription(customer_id: str, price_id: str, trial_period_days: int=0, raw=False):
    if trial_period_days > 0:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                "price": price_id,
            }],
            trial_period_days=trial_period_days,
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            trial_settings={"end_behavior": {"missing_payment_method": "create_invoice"}}, # or "cancel" or "pause"
            expand=["latest_invoice.payment_intent"],
        )
    else:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                "price": price_id,
            }],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
        )
    if raw:
        return subscription
    
    current_period_start = utils.timestamp_as_datetime(subscription.current_period_start)
    current_period_end = utils.timestamp_as_datetime(subscription.current_period_end)

    response = {
        "stripe_id": subscription.id, 
        "client_secret": subscription.latest_invoice.payment_intent.client_secret,
        # "payment_method": subscription.latest_invoice.payment_intent.payment_method,
        "current_period_start": current_period_start,
        "current_period_end": current_period_end,
        "status": subscription.status,
    }
    return response


def update_subscription(stripe_id: str, new_price_id: str, raw=False):
    subscription = stripe.Subscription.retrieve(stripe_id)

    response = stripe.Subscription.modify(
        stripe_id,
        cancel_at_period_end=False,
        items=[{
            "id": subscription["items"]["data"][0].id,
            "price": new_price_id,
        }]
    )
    if raw:
        return response
    
    current_period_start = utils.timestamp_as_datetime(subscription.current_period_start)
    current_period_end = utils.timestamp_as_datetime(subscription.current_period_end)

    return {
        "stripe_id": response.id, 
        "client_secret": response.latest_invoice.payment_intent.client_secret,
        # "payment_method": response.latest_invoice.payment_intent.payment_method,
        "current_period_start": current_period_start,
        "current_period_end": current_period_end, 
        "status": subscription.status,
    }


def cancel_subscription(
        stripe_id: str, reason: str="", 
        cancel_at_period_end: bool=False, 
        feedback: str="other", raw=False
    ):
    if cancel_at_period_end:
        response = stripe.Subscription.cancel(
            stripe_id,
            cancel_at_period_end=cancel_at_period_end,
            cancellation_details={
                "comment": reason,
                "feedback": feedback
            }
        )
    else:
        response = stripe.Subscription.cancel(
            stripe_id,
            cancellation_details={
                "comment": reason,
                "feedback": feedback
            }
        )
    if raw:
        return response
    
    current_period_start = utils.timestamp_as_datetime(response.current_period_start)
    current_period_end = utils.timestamp_as_datetime(response.current_period_end)

    return {
        "stripe_id": response.id, 
        "current_period_start": current_period_start,
        "current_period_end": current_period_end, 
        "status": response.status,
        "cancel_at_period_end": response.cancel_at_period_end,
    }


def delete_subscription(stripe_id: str, raw=False):
    response = stripe.Subscription.delete(stripe_id)
    if raw:
        return response
    return response.id


def get_payment_method(payment_id, raw=False):
    response = stripe.PaymentMethod.retrieve(payment_id)
    if raw:
        return response
    resp = {
        "id": response.id,
        "last4": response.last4,
        "exp_month": response.exp_month,
        "exp_year": response.exp_year,
    }
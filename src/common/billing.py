import json
import stripe
from django.conf import settings

from common import date_utils

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


def create_checkout_session(
    customer_id, 
    success_url="", 
    cancel_url="", 
    price_stripe_id="", 
    trial_period_days=0,
    raw=True
):
    if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
        success_url = f"{success_url}" + "?session_id={CHECKOUT_SESSION_ID}"
    
    if trial_period_days > 0:
        response= stripe.checkout.Session.create(
            customer=customer_id,
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[{"price": price_stripe_id, "quantity": 1}],
            subscription_data={
                "trial_settings": {"end_behavior": {"missing_payment_method": "cancel"}},
                "trial_period_days": trial_period_days,
            },
            payment_method_collection="if_required",
            mode="subscription",
        )
    else:
        response= stripe.checkout.Session.create(
            customer=customer_id,
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[{"price": price_stripe_id, "quantity": 1}],
            mode="subscription",
        )
    if raw:
        return response
    return response.url


def serialize_subscription_data(subscription_response):
    status = subscription_response.status
    current_period_start = date_utils.timestamp_as_datetime(subscription_response.current_period_start)
    current_period_end = date_utils.timestamp_as_datetime(subscription_response.current_period_end)
    cancel_at_period_end = subscription_response.cancel_at_period_end
    return {
        "current_period_start": current_period_start,
        "current_period_end": current_period_end,
        "status": status,
        "cancel_at_period_end": cancel_at_period_end,
    }


def get_checkout_session(stripe_id, raw=True):
    response =  stripe.checkout.Session.retrieve(
            stripe_id
        )
    if raw:
        return response
    return response.url


def get_checkout_customer_plan(session_id):
    checkout_r = get_checkout_session(session_id, raw=True)
    customer_id = checkout_r.customer
    sub_stripe_id = checkout_r.subscription
    sub_r = get_subscription(sub_stripe_id, raw=True)
    # current_period_start
    # current_period_end
    sub_plan = sub_r.plan
    subscription_data = serialize_subscription_data(sub_r)
    data = {
        "customer_id": customer_id,
        "plan_id": sub_plan.id,
        "sub_stripe_id": sub_stripe_id,
       **subscription_data,
    }
    return data


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
    
    current_period_start = date_utils.timestamp_as_datetime(subscription.current_period_start)
    current_period_end = date_utils.timestamp_as_datetime(subscription.current_period_end)

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
    
    current_period_start = date_utils.timestamp_as_datetime(subscription.current_period_start)
    current_period_end = date_utils.timestamp_as_datetime(subscription.current_period_end)

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
        response = stripe.Subscription.modify(
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
    return serialize_subscription_data(response)


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
    return resp


def get_customer_active_subscriptions(customer_stripe_id):
    response = stripe.Subscription.list(
        customer=customer_stripe_id,
        status="active"
    )
    print(response)
    return response


def get_subscription(stripe_id, raw=True):
    response =  stripe.Subscription.retrieve(
            stripe_id
        )
    if raw:
        return response
    return serialize_subscription_data(response)


def create_customer_portal(
        customer_stripe_id: str, 
        return_url: str="", 
        raw: bool=False
    ):
    session = stripe.billing_portal.Session.create(
        customer=customer_stripe_id,
        return_url=return_url,
    )
    if raw:
        return session
    return session.url


def get_stripe_webhook_event(request):
    print(request.data)

    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    request_data = json.loads(request.data)

    if webhook_secret:
        signature = request.headers.get("stripe-signature")
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data,
                sig_header=signature,
                secret=webhook_secret
            )
            print(event)
            data = event["data"]
        except Exception as e:
            return e
        
        event_type = event["type"]
    else:
        data = request_data["data"]
        event_type = request_data["type"]
    return {"data": data, "event_type": event_type}


def delete_subscription(product_id, raw: bool=False):
    response = stripe.Product.delete(product_id)
    if raw:
        return response
    return response.id


def deactivate_price(price_id, raw: bool=False):
    response = stripe.Price.modify(
        price_id,
        active=False,
    )
    if raw:
        return response
    return response.id
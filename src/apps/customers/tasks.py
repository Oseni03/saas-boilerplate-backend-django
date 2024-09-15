from apps.aws_tasks.utils import lambda_task
from apps.subscriptions.models import SubscriptionPrice, UserSubscription
from common import billing


@lambda_task
def create_user_free_subscription(customer):
    price = SubscriptionPrice.objects.filter(trial_period_days__gt=0).first()
    stripe_sub = billing.create_subscription(
        customer.stripe_id,
        price_id=price.stripe_id,
        trial_period_days=price.trial_period_days,
    )
    UserSubscription.objects.create(
        user=customer.user,
        stripe_id=stripe_sub.get("stripe_id"),
        status=stripe_sub.get("status"),
        current_period_start=stripe_sub.get("current_period_start"),
        current_period_end=stripe_sub.get("current_period_end"),
        subscription=price.subscription,
    )
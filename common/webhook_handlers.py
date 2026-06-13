from apps.subscriptions.models import SubscriptionStatus, UserSubscription


def handle_subscription_update(subscription):
    user_subscription = UserSubscription.objects.get(stripe_id=subscription['id'])
    user_subscription.status = subscription['status']
    user_subscription.current_period_end = subscription['current_period_end']
    user_subscription.save()


def handle_subscription_deletion(subscription):
    user_subscription = UserSubscription.objects.get(stripe_id=subscription['id'])
    user_subscription.status = SubscriptionStatus.CANCELED
    user_subscription.active = False
    user_subscription.save()


def handle_subscription_paused(subscription):
    user_subscription = UserSubscription.objects.get(stripe_id=subscription['id'])
    user_subscription.status = SubscriptionStatus.PAUSED
    user_subscription.active = False
    user_subscription.save()
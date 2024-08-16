from datetime import datetime
from apps.subscriptions.models import Subscription, UserSubscription
from apps.customers.models import Customer
from django.contrib.auth.models import Group, Permission
from common import billing
from . import constants


def timestamp_as_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, tz=datetime.UTC)


def clear_dangling_subs() -> str | None:
    customers = Customer.objects.filter(stripe_id__isnull=False)
    for cus_obj in customers:
        user = cus_obj.user
        customer_stripe_id = cus_obj.stripe_id
        subs = billing.get_customer_active_subscriptions(customer_stripe_id)
        for sub in subs:
            existing_user_subs = UserSubscription.objects.filter(
                stripe_id__iexact=f"{sub.id}".strip()
            )
            print(sub.id, existing_user_subs.exists())
            if existing_user_subs.exists():
                billing.cancel_subscription(
                    sub.id, 
                    reason="Canceling dangling active subscriptions", 
                    cancel_at_period_end=True
                )


def init_permissions():
    for plan in constants.subscription_plan_groups:
        group, _ = Group.objects.get_or_create(name=plan.lower())
        if plan == constants.SubscriptionPlanGroups.Advance:
            group.permissions.add(
                Permission.objects.get(codename=constants.CommomPermissions.Advance),
                Permission.objects.get(codename=constants.CommomPermissions.Pro),
                Permission.objects.get(codename=constants.CommomPermissions.Basic),
            )
        elif plan == constants.SubscriptionPlanGroups.Pro:
            group.permissions.add(
                Permission.objects.get(codename=constants.CommomPermissions.Pro),
                Permission.objects.get(codename=constants.CommomPermissions.Basic),
            )
        elif plan == constants.SubscriptionPlanGroups.Basic:
            group.permissions.add(
                Permission.objects.get(codename=constants.CommomPermissions.Basic)
            )
        
        group.save()


def sync_subs() -> str | None:
    qs = Subscription.objects.filter(active=True)
    for obj in qs:
        sub_perms = obj.permissions.all()
        for group in obj.groups.all():
            group.permissions.set(sub_perms)

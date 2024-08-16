from apps.subscriptions.models import Subscription, UserSubscription
from apps.customers.models import Customer
from django.contrib.auth.models import Group, Permission
from common import billing
from . import constants


def refresh_users_subscriptions(user_ids=None, active_only=True):
    qs = UserSubscription.objects.all().by_active()
    if active_only:
        qs = qs.by_active()
    if user_ids is not None:
        qs = qs.by_user_ids(user_ids)
    
    complete_count = 0
    qs_count = qs.count()
    for obj in qs:
        if obj.stripe_id:
            sub_data = billing.get_subscription(obj.stripe_id, raw=False)
            for k, v in sub_data.items():
                setattr(obj, k, v)
            obj.save()
            complete_count += 1
    return complete_count == qs_count


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

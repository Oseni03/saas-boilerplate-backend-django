from typing import Any
from django.core.management.base import BaseCommand

from apps.subscriptions.models import UserSubscription
from apps.customers.models import Customer

from common import billing


class Command(BaseCommand):
    """Can be run once a month"""

    def handle(self, *args: Any, **options: Any) -> str | None:
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
import hashid_field
import logging
from stripe.error import AuthenticationError
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from apps.subscriptions.models import SubscriptionPrice, UserSubscription
from common import billing

from apps.users.signals import email_confirmed_signal
from common import billing

logger = logging.getLogger(__name__)

User = get_user_model()


# Create your models here.
class Customer(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer"
    )
    stripe_id = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.user)

    def save(self, *args, **kwargs) -> None:
        if not self.stripe_id:
            stripe_id = billing.create_customer(
                email=self.user.email, metadata={"user_id": self.user.id}
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)


def create_customer_callback(sender, instance, *args, **kwargs):
    Customer.objects.create(user=instance)


email_confirmed_signal.connect(create_customer_callback, User)


def create_free_plan_subscription(sender, instance, created, **kwargs):
    """
    Primary purpose for separating this code into its own function is the ability to mock it during tests so we utilise
    a schedule created by factories instead of relying on stripe-mock response

    :param user:
    :return:
    """
    if not settings.STRIPE_ENABLED:
        return

    if created:
        try:
            price = SubscriptionPrice.objects.filter(trial_period_days__gt=0).first()
            stripe_sub = billing.create_subscription(
                instance.stripe_id,
                price_id=price.stripe_id,
                trial_period_days=price.trial_period_days,
            )
            UserSubscription.objects.create(
                user=instance.user,
                stripe_id=stripe_sub.get("stripe_id"),
                status=stripe_sub.get("status"),
                current_period_start=stripe_sub.get("current_period_start"),
                current_period_end=stripe_sub.get("current_period_end"),
                subscription=price.subscription,
            )
        except AuthenticationError as e:
            logger.error(msg=e._message, exc_info=e)
            return
        except Exception as e:
            raise e


post_save.connect(create_free_plan_subscription, Customer)

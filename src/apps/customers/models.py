import hashid_field
import logging
from stripe.error import AuthenticationError
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from apps.aws_tasks.utils import get_task_name, send_task_to_sqs
from apps.customers.tasks import create_user_free_subscription

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
            task_name = get_task_name(create_user_free_subscription)
            send_task_to_sqs(task_name=task_name, customer=instance)
        except AuthenticationError as e:
            logger.error(msg=e._message, exc_info=e)
            return
        except Exception as e:
            raise e


post_save.connect(create_free_plan_subscription, Customer)

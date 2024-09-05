import hashid_field
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.users.signals import email_confirmed_signal
from common import billing

User = get_user_model()


# Create your models here.
class Customer(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer")
    stripe_id = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.user)
    
    def save(self, *args, **kwargs) -> None:
        if not self.stripe_id:
            stripe_id = billing.create_customer(
                email=self.user.email,
                metadata={"user_id": self.user.id}
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)


def create_customer_callback(sender, instance, *args, **kwargs):
    Customer.objects.create(user=instance)

email_confirmed_signal.connect(create_customer_callback, User)
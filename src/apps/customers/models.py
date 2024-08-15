import hashid_field
from django.db import models
from django.conf import settings

from common import billing


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


class PaymentMethod(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_methods")
    last4 = models.CharField(max_length=10)
    exp_month = models.CharField(max_length=10)
    exp_year = models.CharField(max_length=10)
    stripe_id = models.CharField(max_length=150, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user}: {self.last4} - {self.exp_month} - {self.exp_year}"
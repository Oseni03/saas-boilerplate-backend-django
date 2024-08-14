from django.db import models
from django.conf import settings

from common import billing


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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

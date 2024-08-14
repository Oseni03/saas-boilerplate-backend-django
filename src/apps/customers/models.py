from django.db import models
from django.conf import settings


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.user)
from django.db import models

from .constants import CommomPermissions

# Create your models here.
class Subscriptions(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        permissions = [
            (CommomPermissions.Advance, "Advanced Perm"), # subscriptions.advanced
            (CommomPermissions.Pro, "Pro Perm"), # subscriptions.pro
            (CommomPermissions.Basic, "Basic Perm"), # subscriptions.basic
        ]
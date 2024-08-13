from django.db import models
from django.contrib.auth.models import Group, Permission

from .constants import CommomPermissions


SUBSCRIPTION_PERMISSIONS =[
    (CommomPermissions.Advance, "Advanced Perm"), # subscriptions.advanced
    (CommomPermissions.Pro, "Pro Perm"), # subscriptions.pro
    (CommomPermissions.Basic, "Basic Perm"), # subscriptions.basic
]

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=120)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(
        Permission, 
        limit_choices_to={
            "content_type__app_label": "subscriptions", 
            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]}
    )

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
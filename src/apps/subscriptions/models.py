from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import Group, Permission

from .constants import CommomPermissions

User = settings.AUTH_USER_MODEL


SUBSCRIPTION_PERMISSIONS =[
    (CommomPermissions.Advance, "Advanced Perm"), # subscriptions.advanced
    (CommomPermissions.Pro, "Pro Perm"), # subscriptions.pro
    (CommomPermissions.Basic, "Basic Perm"), # subscriptions.basic
]

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=120)
    groups = models.ManyToManyField(Group)
    active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        Permission, 
        limit_choices_to={
            "content_type__app_label": "subscriptions", 
            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]}
    )

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
    
    def __str__(self) -> str:
        return str(self.name)


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user}: {self.subscription}"


def user_sub_post_save(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    print(user_sub_instance)
    subscription_obj = user_sub_instance.subscription
    groups = subscription_obj.groups.all()
    user.groups.set(groups)


post_save.connect(user_sub_post_save, UserSubscription)
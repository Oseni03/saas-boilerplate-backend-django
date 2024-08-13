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
    subscription_obj = user_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list("id", flat=True)
    if not settings.ALLOW_CUSTOM_GROUP:
        # If user does not belong to any other type of group 
        # apart from subscription groups, then set the user group only to the 
        # group of the newly subscribed subscription
        user.groups.set(groups)
    else:
        # Set the user group to the combination of any other type of group the user might belong to 
        # and the only to the newly subscribed subscription

        # To get the list of all subscription except for the newly subscribed one
        subs_qs = Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        # To get the list of group ids for each of the subscription above
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)
        # groups_ids = groups.values_list("id", flat=True) # [1,2,3]
        current_groups = user.groups.all().values_list("id", flat=True)
        groups_ids_set = set(groups_ids)
        current_groups_set = set(current_groups) - subs_groups_set
        final_group_ids = list(groups_ids_set | current_groups_set)
        user.groups.set(final_group_ids)


post_save.connect(user_sub_post_save, UserSubscription)
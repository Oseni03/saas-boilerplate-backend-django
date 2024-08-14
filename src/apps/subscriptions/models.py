import hashid_field
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import Group, Permission

from common import billing

from .constants import CommomPermissions

User = settings.AUTH_USER_MODEL


SUBSCRIPTION_PERMISSIONS =[
    (CommomPermissions.Advance, "Advanced Perm"), # subscriptions.advanced
    (CommomPermissions.Pro, "Pro Perm"), # subscriptions.pro
    (CommomPermissions.Basic, "Basic Perm"), # subscriptions.basic
]

# Create your models here.
class Subscription(models.Model):
    """ 
    Subscription = Stripe Product
    """
    id: str = hashid_field.HashidAutoField(primary_key=True)
    name = models.CharField(max_length=120)
    groups = models.ManyToManyField(Group)
    active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        Permission, 
        limit_choices_to={
            "content_type__app_label": "subscriptions", 
            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]}
    )
    stripe_id = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
    
    def __str__(self) -> str:
        return str(self.name)
    
    def save(self, *args, **kwargs) -> None:
        if not self.stripe_id:
            stripe_id = billing.create_product(
                name=self.name,
                metadata={"subscription_plan_id": self.id},
                raw=False
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)


class SubscriptionPrice(models.Model):
    """ 
    Subscription price = Stripe Price
    """
    class SubscriptionCurrency(models.TextChoices):
        DOLLAR = ("usd"), ("USD")
        EURO = ("euro"), ("EURO") # Not Sure if correct

    class SubscriptionInterval(models.TextChoices):
        MONTHLY = ("month"), ("Monthly")
        YEARLY = ("year"), ("Yearly")
        DAILY = ("day"), ("Daily")
        WEEKLY = ("week"), ("Weekly")

    id: str = hashid_field.HashidAutoField(primary_key=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.CharField(
        max_length=15, 
        choices=SubscriptionCurrency.choices, 
        default=SubscriptionCurrency.DOLLAR
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interval = models.CharField(
        max_length=25, 
        choices=SubscriptionInterval.choices, 
        default=SubscriptionInterval.MONTHLY
    )
    trial_period_days = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)
    stripe_id = models.CharField(max_length=150, null=True)
    
    def __str__(self) -> str:
        return str(self.subscription)
    
    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id
    
    @property
    def strip_amount(self):
        """ remove decimal places for stripe"""
        return self.amount * 100
    
    def save(self, *args, **kwargs) -> None:
        if not self.stripe_id and self.product_stripe_id:
            stripe_id = billing.create_price(
                currency=self.currency,
                unit_amount=self.strip_amount,
                interval=self.interval,
                trial_period_days=self.trial_period_days,
                product=self.product_stripe_id,
                metadata={"subscription_price_id": self.id},
                raw=False
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)


class UserSubscription(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
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
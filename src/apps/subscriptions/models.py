import hashid_field
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import Group, Permission

from common import billing

from .managers import UserSubscriptionManger

User = settings.AUTH_USER_MODEL


# Create your models here.
class Subscription(models.Model):
    """
    Subscription = Stripe Product
    """

    id: str = hashid_field.HashidAutoField(primary_key=True)
    name = models.CharField(max_length=120)
    subtitle = models.TextField(null=True, blank=True)
    groups = models.ManyToManyField(Group)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=1)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={
            "content_type__app_label": "subscriptions",
            "codename__in": [x[0] for x in settings.SUBSCRIPTION_PERMISSIONS],
        },
    )
    features = models.TextField(
        help_text="Features for pricing separated by new line", blank=True, null=True
    )
    stripe_id = models.CharField(max_length=150, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-updated"]
        permissions = settings.SUBSCRIPTION_PERMISSIONS

    def __str__(self) -> str:
        return str(self.name)

    @property
    def features_list(self):
        return [x.strip() for x in self.features.split("\n")]

    def save(self, *args, **kwargs) -> None:
        if not self.stripe_id:
            stripe_id = billing.create_product(
                name=self.name, metadata={"subscription_plan_id": self.id}, raw=False
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.stripe_id:
            billing.delete_subscription(self.stripe_id)
        super().delete(*args, **kwargs)


class SubscriptionPrice(models.Model):
    """
    Subscription price = Stripe Price
    """

    class SubscriptionCurrency(models.TextChoices):
        DOLLAR = ("usd"), ("USD")
        EURO = ("euro"), ("EURO")  # Not Sure if correct

    class SubscriptionInterval(models.TextChoices):
        MONTHLY = ("month"), ("Monthly")
        YEARLY = ("year"), ("Yearly")
        DAILY = ("day"), ("Daily")
        WEEKLY = ("week"), ("Weekly")

    id: str = hashid_field.HashidAutoField(primary_key=True)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True
    )
    currency = models.CharField(
        max_length=15,
        choices=SubscriptionCurrency.choices,
        default=SubscriptionCurrency.DOLLAR,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interval = models.CharField(
        max_length=50,
        choices=SubscriptionInterval.choices,
        default=SubscriptionInterval.MONTHLY,
    )
    trial_period_days = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=1, help_text="Ordering on Django pricing page")
    featured = models.BooleanField(
        default=True, help_text="Featured on Django pricing page"
    )
    stripe_id = models.CharField(max_length=150, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["subscription__order", "order", "featured", "-updated"]

    def __str__(self) -> str:
        return str(self.subscription)

    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id

    @property
    def strip_amount(self):
        """remove decimal places for stripe"""
        return int(self.amount * 100)

    def save(self, *args, **kwargs) -> None:
        if not self.stripe_id and self.product_stripe_id is not None:
            stripe_id = billing.create_price(
                currency=self.currency,
                unit_amount=self.strip_amount,
                interval=self.interval,
                trial_period_days=self.trial_period_days,
                product=self.product_stripe_id,
                metadata={"subscription_price_id": self.id},
                raw=False,
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(
                subscription=self.subscription, interval=self.interval
            ).exclude(id=self.id)
            qs.update(featured=False)


class SubscriptionStatus(models.TextChoices):
    INCOMPLETE = "incomplete", _("Incomplete")
    INCOMPLETE_EXPIRED = "incomplete_expired", _("Incomplete Expired")
    TRIALING = "trialing", _("Trialing")
    ACTIVE = "active", _("Active")
    PAST_DUE = "past_due", _("Past Due")
    CANCELED = "canceled", _("canceled")
    UNPAID = "unpaid", _("Unpaid")
    PAUSED = "paused", _("Paused")


class UserSubscription(models.Model):
    """
    User Subscription = Stripe Subscription
    """

    id: str = hashid_field.HashidAutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="subscription"
    )
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True
    )
    active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=30,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )

    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    current_period_start = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    current_period_end = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    cancel_at_period_end = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = UserSubscriptionManger()

    def __str__(self) -> str:
        return f"{self.user}: {self.subscription}"

    @property
    def is_active_status(self):
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    @property
    def billing_cycle_anchor(self):
        """
        Optional delay to start subscription in Stripe

        https://docs.stripe.com/payments/checkout/billing-cycle
        """
        if not self.current_period_end:
            return None
        return int(self.current_period_end.timestamp())

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        if self.stripe_id:
            billing.cancel_subscription(self.stripe_id, reason="Subscription deleted")
        return super().delete(*args, **kwargs)


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
        # and to the newly subscribed subscription group(s)

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


def user_sub_post_delete(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user

    # Set the user group to ther other type of group the user might belong to
    # excluding all active subscription group

    # To get the list of all active subscriptions
    subs_qs = Subscription.objects.filter(active=True)
    # To get the list of group ids for each of the subscriptions above
    subs_groups = subs_qs.values_list("groups__id", flat=True)
    subs_groups_set = set(subs_groups)
    # To get the list of group ids the user belongs to
    current_groups = user.groups.all().values_list("id", flat=True)
    final_group_ids = set(current_groups) - subs_groups_set
    user.groups.set(final_group_ids)


post_delete.connect(user_sub_post_delete, UserSubscription)
import datetime
from django.db import models
from django.utils import timezone


class UserSubscriptionQuerySet(models.QuerySet):
    def by_range(self, days_start: int=7, days_end: int=120):
        now = timezone.now()
        days_start_from_now = now + datetime.timedelta(days=days_start)
        days_end_from_now = now + datetime.timedelta(days=days_end)
        range_start = days_start_from_now.replace(hour=0, second=0, microsecond=0)
        range_end = days_end_from_now.replace(hour=23, second=59, microsecond=59)
        return self.filter(
            current_period_end__gte=range_start,
            current_period_end__lte=range_end,
        )
    
    def by_days_left(self, days_left: int=7):
        now = timezone.now()
        in_n_days = now + datetime.timedelta(days=days_left)
        day_start = in_n_days.replace(hour=0, second=0, microsecond=0)
        day_end = in_n_days.replace(hour=23, second=59, microsecond=59)
        return self.filter(
            current_period_end__gte=day_start,
            current_period_end__lte=day_end,
        )
    
    def by_days_ago(self, days_ago: int=3):
        now = timezone.now()
        in_n_days = now - datetime.timedelta(days=days_ago)
        day_start = in_n_days.replace(hour=0, second=0, microsecond=0)
        day_end = in_n_days.replace(hour=23, second=59, microsecond=59)
        return self.filter(
            current_period_end__gte=day_start,
            current_period_end__lte=day_end,
        )

    def by_active(self):
        from .models import SubscriptionStatus
        
        active_qs_lookup = (
            models.Q(status=SubscriptionStatus.ACTIVE) |
            models.Q(status=SubscriptionStatus.TRIALING)
        )
        return self.filter(active_qs_lookup)
    
    def by_user_ids(self, user_ids=None):
        qs = self
        if isinstance(user_ids, list):
            qs = qs.filter(user_id__in=user_ids)
        elif isinstance(user_ids, str):
            qs = qs.filter(user_id__in=[user_ids])
        elif isinstance(user_ids, int):
            qs = qs.filter(user_id__in=[user_ids])
        return qs


class UserSubscriptionManger(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return UserSubscriptionQuerySet(self.model, using=self._db)
    
    def by_user_ids(self, user_ids=None):
        qs = self.get_queryset()
        if isinstance(user_ids, list):
            qs = qs.filter(user_id__in=user_ids)
        elif isinstance(user_ids, str):
            qs = qs.filter(user_id__in=[user_ids])
        elif isinstance(user_ids, int):
            qs = qs.filter(user_id__in=[user_ids])
        return qs
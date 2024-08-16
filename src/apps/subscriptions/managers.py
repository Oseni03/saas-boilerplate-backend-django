from django.db import models

from .models import SubscriptionStatus


class UserSubscriptionQuerySet(models.QuerySet):
    def by_active(self):
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
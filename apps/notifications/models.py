import datetime
from typing import Optional

import hashid_field
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _

from . import managers


class NotificationType(models.TextChoices):
    UPDATE_PROFILE = "UPDATE_PROFILE", _("Update Profile")
    DEFAULT = "DEFAULT", _("Default")


class Notification(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    user: settings.AUTH_USER_MODEL = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # type: ignore
    type: str = models.CharField(
        max_length=64,
        choices=NotificationType.choices,
        default=NotificationType.DEFAULT,
    )
    title: str = models.CharField(max_length=255)
    description: str = models.TextField(blank=True, null=True)

    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    read_at: Optional[datetime.datetime] = models.DateTimeField(null=True, blank=True)

    data: dict = models.JSONField(default=dict, null=True, blank=True)

    issuer: settings.AUTH_USER_MODEL = models.ForeignKey(  # type: ignore
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications_issued",
    )

    objects = managers.NotificationManager()

    def __str__(self) -> str:
        return str(self.id)

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    @property
    def timesince(self):
        now = timezone.now()
        return f"{timesince(self.created_at, now=now)} ago"

    @is_read.setter
    def is_read(self, val: bool):
        self.read_at = timezone.now() if val else None


class NotificationPreference(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preference",
    )
    email_notification = models.BooleanField(default=True)
    push_notification = models.BooleanField(default=False)
    inapp_notification = models.BooleanField(default=False)
    sms_notification = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

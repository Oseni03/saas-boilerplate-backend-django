from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.dispatch import receiver

from apps.users.models import UserProfile

from . import models, serializers 
from .sender import send_notification


@receiver(post_save, sender=models.Notification)
def notify_about_entry(sender, instance: models.Notification, created, update_fields, **kwargs):
    if created:
        # schema.NotificationCreatedSubscription.broadcast(payload={'id': str(instance.id)}, group=str(instance.user.id))
        serialized_notification = serializers.NotificationSerializer(instance)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            instance.user.id,
            {
                'id': instance.id,
                'type': instance.type,
                'notification': serialized_notification.data
            }
        )


@receiver(post_save, sender=models.NotificationPreference)
def notify_about_update_requirements(sender, instance: models.NotificationPreference, created, update_fields, **kwargs):
    if not created:
        profile = UserProfile.objects.get(user=instance.user)
        if instance.push_notification and not profile.device_token:
            pass
        if instance.sms_notification and not profile.phone_number:
            send_notification(
                instance.user, 
                models.NotificationType.UPDATE_PROFILE, 
                "Update your profile phone number."
            )
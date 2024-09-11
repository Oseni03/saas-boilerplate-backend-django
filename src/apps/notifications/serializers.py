from hashid_field import rest as hidrest
from rest_framework import serializers

from apps.users.models import UserProfile

from . import models


class NotificationSerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(
        source_field="notifications.Notification.id", source="notification.id", read_only=True
    )
    class Meta:
        model = models.Notification
        fields = ("id", "type", "message", "is_read", "created_at", "data", "issuer")


class UpdateNotificationSerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(
        source_field="notifications.Notification.id", source="notification.id", read_only=True
    )
    is_read = serializers.BooleanField(required=False)

    def update(self, instance: models.Notification, validated_data: dict):
        is_read = validated_data["is_read"]
        if is_read != instance.is_read:
            instance.is_read = is_read
            instance.save(update_fields=["read_at"])
        return instance

    class Meta:
        model = models.Notification
        fields = ("id", "is_read")


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(
        source_field="notifications.NotificationPreference.id", read_only=True
    )
    class Meta:
        model = models.NotificationPreference
        fields = (
            "id", "email_notification", 
            "inapp_notification", 
            "push_notification", 
            "sms_notification", 
            "updated_at"
        )
    
    def validate_push_notification(self, value):
        user = self.context["request"].user
        profile = UserProfile.objects.get(user=user)
        if value is True and not profile.device_token:
            raise serializers.ValidationError("Setup push notification")
        return value

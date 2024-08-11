from rest_framework import serializers


class NotificationType(serializers.Serializer):
    user_id = serializers.CharField()
    type = serializers.CharField()
    message = serializers.CharField()

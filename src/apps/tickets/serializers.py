from hashid_field import rest as hidrest
from rest_framework import serializers

from .models import Ticket


class FeedbackSerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(
        source_field="tickets.Ticket.id", read_only=True
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    type = serializers.HiddenField(default="feedback")

    class Meta:
        model = Ticket
        fields = [
            "id", "user", "title", "message", "type", 
            "rating", "created_at"
        ]
        read_only_fields = ('created_at',)


class SupportSerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(
        source_field="tickets.Ticket.id", read_only=True
    )
    type = serializers.HiddenField(default="issue")

    class Meta:
        model = Ticket
        fields = [
            "id", "email", "full_name", "title", "message", "type", "created_at"
        ]
        read_only_fields = ('created_at',)
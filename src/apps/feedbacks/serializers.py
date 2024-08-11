from hashid_field import rest as hidrest
from rest_framework import serializers

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(
        source_field="feedbacks.Feedback.id", read_only=True
    )

    class Meta:
        model = Feedback
        fields = ["id", "message", "rating", "created_at"]
        read_only_fields = ('user', 'created_at')
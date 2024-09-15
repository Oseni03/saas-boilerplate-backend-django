from hashid_field import rest
from rest_framework import serializers

from .models import TaskResult

class TaskSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)

    class Meta:
        model = TaskResult
        fields = "__all__"
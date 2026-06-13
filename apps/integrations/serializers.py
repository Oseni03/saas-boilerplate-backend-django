from rest_framework import serializers
from hashid_field import rest
from .models import Thirdparty, Integration


class ThirdpartySerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)
    is_connected = serializers.SerializerMethodField()
    integration_id = serializers.SerializerMethodField()

    class Meta:
        model = Thirdparty
        fields = (
            "id",
            "name",
            "description",
            "is_connected",
            "slug",
            "oauth_url",
            "integration_id"
        )

    def get_is_connected(self, obj: Thirdparty):
        user = self.context["request"].user  # Get current user
        return Integration.objects.filter(thirdparty=obj, user=user).exists()

    def get_integration_id(self, obj: Thirdparty):
        user = self.context["request"].user  # Get current user
        integrations = Integration.objects.filter(thirdparty=obj, user=user)
        if integrations.exists():
            return str(integrations.first().id)
        return None


class IntegrationSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)
    thirdparty = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Thirdparty.objects.filter(is_active=True),
        write_only=True,
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    code = serializers.CharField(write_only=True, required=False)
    state = serializers.CharField(write_only=True, required=False)
    oauth_url = serializers.SerializerMethodField()

    class Meta:
        model = Integration
        fields = (
            "id",
            "thirdparty",
            "user",
            "code",
            "state",
            "access_token",
            "refresh_token",
            "webhook_url",
            "expires_at",
            "oauth_url",
        )
        read_only_fields = (
            "access_token",
            "refresh_token",
            "webhook_url",
            "expires_at",
            "oauth_url",
        )

    def get_oauth_url(self, obj: Integration):
        return obj.get("oauth_url")


class OAuthCallbackSerializer(serializers.Serializer):
    state = serializers.CharField()
    code = serializers.CharField()
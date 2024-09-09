from datetime import timedelta, timezone
from rest_framework import serializers
from hashid_field import rest
from .models import Thirdparty, Integration


class ThirdpartySerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_connected = serializers.SerializerMethodField()

    class Meta:
        model = Thirdparty
        fields = (
            "id",
            "name",
            "description",
            "is_connected",
            "slug",
            "oauth_url",
            "user",
        )

    def get_is_connected(self, obj: Thirdparty):
        user = self.context["request"].user  # Get current user
        return Integration.objects.filter(
            thirdparty=obj, user=user, is_active=True
        ).exists()


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

    def create(self, validated_data):
        thirdparty: Thirdparty = validated_data["thirdparty"]
        code = validated_data.get("code", "")
        state = validated_data.get("state", "")
        user = validated_data["user"]

        if state:
            if state != thirdparty.state:
                raise serializers.ValidationError("Invalid request")

        integration, created = Integration.objects.get_or_create(
            thirdparty=thirdparty, user=user
        )

        if not code and created:
            return {"oauth_url": thirdparty.oauth_url}
        else:
            try:
                resp = thirdparty.handle_oauth_callback(code)
            except:
                raise serializers.ValidationError("Invalid code")

            integration.access_token = resp.get("access_token")
            integration.refresh_token = resp.get("refresh_token")
            integration.expires_at = timezone.now() + timedelta(
                seconds=int(resp.get("expires_in", 3600))
            )
            integration.is_active = True

        return integration

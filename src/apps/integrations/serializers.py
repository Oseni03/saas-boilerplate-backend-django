from datetime import timedelta, timezone
from hashid_field import rest
from rest_framework import serializers

from common.date_utils import convert_timezone_to_datetime

from .models import Thirdparty, Integrations


class ThirdpartySerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)

    class Meta:
        model = Thirdparty
        fields = ("id", "name", "slug", "oauth_url")


class CreateIntegrationSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)
    thirdparty = serializers.PrimaryKeyRelatedField(
        queryset=Thirdparty.objects.filter(is_active=True),
        pk_field=rest.HashidSerializerCharField(),
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    code = serializers.CharField(write_only=True)

    class Meta:
        model = Integrations
        fields = (
            "id",
            "thirdparty",
            "user",
            "code",
            "access_token",
            "refresh_token",
            "webhook_url",
            "expires_at",
        )
        read_only_fields = (
            "access_token",
            "refresh_token",
            "webhook_url",
            "expires_at",
        )

    def create(self, validated_data):
        thirdparty = validated_data["thirdparty"]
        code = validated_data["code"]

        try:
            resp = thirdparty.handle_oauth_callback(code)
        except:
            raise serializers.ValidationError("Invalid code")

        resp_tz = timezone.now() + timedelta(
            seconds=int(resp.get("expires_in", None) or resp.get("issued_at"))
        )
        validated_data["access_token"] = resp.get("access_token")
        validated_data["refresh_token"] = resp.get("refresh_token")
        validated_data["expires_at"] =  convert_timezone_to_datetime(resp_tz)  # convert timezone to datatime
        validated_data["webhook_url"] = resp.get("webhook_url")
        return super().create(validated_data)


class IntegrationSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)

    class Meta:
        model = Integrations
        fields = ("id", "thirdparty", "expires_at", "created", "updated")

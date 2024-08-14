from hashid_field import rest
from rest_framework import serializers

from common import billing
from .models import SubscriptionPrice, Subscription, UserSubscription


class SubscriptionSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "name", "subtitle", "features_list"]


class SubscriptionPriceSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)
    Subscription_name = serializers.SerializerMethodField()
    Subscription_subtitle = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    interval_display = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPrice
        fields = [
            "id", "subscription_name", "Subscription_subtitle", 
            "currency", "interval", "order", "features", 
            "trial_period_days", "amount", "interval_display"
        ]

    def get_subscription_name(self, obj: SubscriptionPrice):
        if not obj.subscription:
            return "Plan"
        return obj.subscription.name
    
    def get_features(self, obj: SubscriptionPrice):
        if not obj.subscription:
            return []
        return obj.subscription.features_list
    
    def get_interval_display(self, obj: SubscriptionPrice):
        return obj.get_interval_display()
    
    def get_Subscription_subtitle(self, obj: SubscriptionPrice):
        return obj.subscription.subtitle


class UserSubscriptionSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserSubscription
        fields = ["id", "user", "subscription"]
    
    def create(self, validated_data):
        user = validated_data["user"]
        subscription = validated_data["subscription"]

        response = billing.create_subscription(
            user.customer.stripe_id,
            subscription.stripe_id, # Confirm if it returns the subscription ID or object
            raw=False
        )
        UserSubscription.objects.create(
            user=user, 
            subscription=subscription,
            stripe_id=response["subscription_id"],
        )
        return response
    
    def update(self, instance, validated_data):
        billing.update_subscription(
            instance.stripe_id,
            validated_data["subscription"].id,
            raw=False
        )
        return super().update(instance, validated_data)
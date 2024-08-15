from hashid_field import rest
from rest_framework import serializers
from django.utils.translation import gettext as _

from apps.customers.models import PaymentMethod
from common import billing
from .models import SubscriptionPrice, Subscription, UserSubscription


class SubscriptionSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "name", "subtitle", "features_list"]


class SubscriptionPriceSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)
    subscription_name = serializers.SerializerMethodField()
    subscription_subtitle = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    interval_display = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPrice
        fields = [
            "id", "subscription_name", "subscription_subtitle", 
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
    
    def get_subscription_subtitle(self, obj: SubscriptionPrice):
        return obj.subscription.subtitle


class UserSubscriptionSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    price_id = serializers.CharField(write_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            "id", "user", "price_id", "subscription", 
            "status", "client_secret", "current_period_start", 
            "current_period_end",
        ]
        read_only_fields = [
            "id", "subscription", "status", "client_secret", 
            "current_period_start", "current_period_end"
        ]
    
    def validate(self, attrs):
        price_id = attrs["price_id"]
        try:
            price = SubscriptionPrice.objects.get(id=price_id)
        except:
            raise serializers.ValidationError({'price_id': _('Price with ID not found')})
        attrs["price"] = price
        attrs["subscription"] = price.subscription
        return attrs
    
    def create(self, validated_data):
        user = validated_data["user"]
        subscription = validated_data["subscription"]
        price = validated_data["price"]

        try:
            _user_sub_obj = UserSubscription.objects.get(user)
            _former_sub_id = _user_sub_obj.stripe_id

            response = billing.update_subscription(
                _user_sub_obj.stripe_id,
                price.id,
                raw=False
            )
            _user_sub_obj.subscription = subscription
            _user_sub_obj.stripe_id = response["stripe_id"]
            _user_sub_obj.client_secret = response["client_secret"]
            _user_sub_obj.current_period_start = response["current_period_start"]
            _user_sub_obj.current_period_end = response["current_period_end"]
            _user_sub_obj.status = response["status"]
            _user_sub_obj.save()
            if _former_sub_id and _former_sub_id!=response["stripe_id"]:
                # billing.delete_subscription(_former_sub_id)
                billing.cancel_subscription(_former_sub_id, reason="Switch subscription")
        except UserSubscription.DoesNotExist:
            response = billing.create_subscription(
                customer_id=user.customer.stripe_id,
                trial_period_days=price.trial_period_days,
                price_id=price.stripe_id,
                raw=False
            )
            print(response)

            _user_sub_obj = UserSubscription.objects.create(
                user=user, 
                subscription=subscription,
                stripe_id=response["stripe_id"],
                client_secret=response["client_secret"],
                current_period_start=response["current_period_start"],
                current_period_end=response["current_period_end"],
                status=response["status"],
            )
        except:
            _user_sub_obj = None
        
        if _user_sub_obj is None:
            raise serializers.ValidationError(_('There is an error with your account, please contact us'))

        payment_method = billing.get_payment_method(response["payment_method"])
        print(payment_method)

        PaymentMethod.objects.get_or_create(
            user=user,
            last4=payment_method["last4"],
            exp_month=payment_method["exp_month"],
            exp_year=payment_method["exp_year"],
            stripe_id=payment_method["id"],
        )
        return response
    
    def update(self, instance, validated_data):
        user = validated_data["user"]
        price = validated_data["price"]

        response = billing.update_subscription(
            instance.stripe_id,
            price.id,
            raw=False
        )
        instance.subscription = validated_data["subscription"]
        instance.stripe_id = response["stripe_id"]
        instance.client_secret = response["client_secret"]
        instance.current_period_start = response["current_period_start"]
        instance.current_period_end = response["current_period_end"]
        instance.save()
        payment_method = billing.get_payment_method(response["payment_method"])
        print(payment_method)

        PaymentMethod.objects.get_or_create(
            user=user,
            last4=payment_method["last4"],
            exp_month=payment_method["exp_month"],
            exp_year=payment_method["exp_year"],
            stripe_id=payment_method["id"],
        )
        return response


class PaymentMethodSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)

    class Meta:
        model = PaymentMethod
        fields = ["id", "last4", "exp_month", "exp_year", "updated"]
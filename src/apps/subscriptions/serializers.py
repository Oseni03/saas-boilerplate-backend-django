from hashid_field import rest
from rest_framework import serializers
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.customers.models import PaymentMethod
from common import billing
from .models import SubscriptionPrice, Subscription, UserSubscription

User = get_user_model()

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


class CreateCheckoutSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    price_id = serializers.CharField(write_only=True)

    def validate(self, attrs):
        price_id = attrs["price_id"]
        try:
            price = SubscriptionPrice.objects.get(id=price_id)
        except:
            raise serializers.ValidationError({'price_id': _('Price with ID not found')})
        attrs["price"] = price
        return attrs
    
    def create(self, validated_data):
        price = validated_data["price"]
        customer_stripe_id = validated_data["user"].customer.stripe_id
        success_url_path = settings.CHECKOUT_SUCCESS_URL
        cancel_url_path = settings.CHECKOUT_CANCEL_URL
        success_url = f"{settings.BASE_URL}{success_url_path}"
        cancel_url= f"{settings.BASE_URL}{cancel_url_path}"
        price_stripe_id = price.stripe_id

        url = billing.create_checkout_session(
            customer_stripe_id,
            success_url=success_url,
            cancel_url=cancel_url,
            price_stripe_id=price_stripe_id,
            trial_period_days=price.trial_period_days,
            raw=False
        )
        return url


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """ UserSubscription Serializer"""
    id = rest.HashidSerializerCharField(read_only=True)
    session_id = serializers.CharField(write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = [
            "id", "user", "session_id", "subscription", 
            "status", "current_period_start", 
            "current_period_end",
        ]
        read_only_fields = [
            "id", "user", "subscription", "status", 
            "current_period_start", "current_period_end"
        ]
    
    def get_subscription(self, obj):
        return obj.subscription.name

    def create(self, validated_data):
        user = validated_data('user')
        session_id = validated_data('session_id')
        checkout_data = billing.get_checkout_customer_plan(session_id)
        plan_id = checkout_data.pop('plan_id')
        customer_id = checkout_data.pop('customer_id')
        sub_stripe_id = checkout_data.pop("sub_stripe_id")
        subscription_data = {**checkout_data}
        try:
            sub_obj = Subscription.objects.get(subscriptionprice__stripe_id=plan_id)
        except:
            sub_obj = None
        if user.customer.stripe_id == customer_id:
            user_obj = user
        else:
            user_obj = None

        _user_sub_exists = False
        updated_sub_options = {
            "subscription": sub_obj,
            "stripe_id": sub_stripe_id,
            "user_cancelled": False,
            **subscription_data,
        }
        try:
            _user_sub_obj = UserSubscription.objects.get(user=user_obj)
            _user_sub_exists = True
        except UserSubscription.DoesNotExist:
            _user_sub_obj = UserSubscription.objects.create(
                user=user_obj, 
                **updated_sub_options
            )
        except:
            _user_sub_obj = None
        if None in [sub_obj, user_obj, _user_sub_obj]:
            return serializers.ValidationError(_("There was an error with your account, please contact us."))
        if _user_sub_exists:
            # cancel old sub
            old_stripe_id = _user_sub_obj.stripe_id
            same_stripe_id = sub_stripe_id == old_stripe_id
            if old_stripe_id is not None and not same_stripe_id:
                try:
                    billing.cancel_subscription(old_stripe_id, reason="Auto ended, new membership", feedback="other")
                except:
                    pass
            # assign new sub
            for k, v in updated_sub_options.items():
                setattr(_user_sub_obj, k, v)
            _user_sub_obj.save()
        return _user_sub_obj


class CancelActiveUserSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSubscription
        fields = ()
    
    def update(self, instance: UserSubscription, validated_data):
        if instance.stripe_id and instance.is_active_status:
            response = billing.cancel_subscription(
                instance.stripe_id, 
                cancel_at_period_end=True,
                reason="User cancel subscription",
            )
        else:
            response = billing.cancel_subscription(
                instance.stripe_id, 
                reason="User cancel subscription",
            )
        for k, v in response.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class PaymentMethodSerializer(serializers.ModelSerializer):
    id = rest.HashidSerializerCharField(read_only=True)

    class Meta:
        model = PaymentMethod
        fields = ["id", "last4", "exp_month", "exp_year", "updated"]
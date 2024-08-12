from rest_framework import generics, permissions
from djstripe import models as djstripe_models

from apps.users.models import UserProfile
from common.permissions import IsSubscribed

from .services import subscriptions

from . import serializers


class CreateSubscriptionView(generics.CreateAPIView):
    serializer_class = serializers.SubscriptionScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChangeActiveSubscriptionView(generics.UpdateAPIView):
    serializer_class = serializers.SubscriptionScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsSubscribed]
    
    def get_object(self):
        return subscriptions.get_schedule(profile=self.request.profile)


class CancelActiveSubscriptionView(generics.UpdateAPIView):
    serializer_class = serializers.CancelActiveSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSubscribed]
    
    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return subscriptions.get_schedule(profile=profile)


class PaymentMethodView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.PaymentMethodSerializer
    
    def get_queryset(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return djstripe_models.PaymentMethod.objects.filter(customer__subscriber=profile)


class CreatePaymentIntentView(generics.CreateAPIView):
    serializer_class = serializers.PaymentIntentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return djstripe_models.PaymentIntent.objects.filter(customer__subscriber=profile)


class UpdatePaymentIntentView(generics.UpdateAPIView):
    serializer_class = serializers.PaymentIntentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return djstripe_models.PaymentIntent.objects.filter(customer__subscriber=profile)


class CreateSetupIntentView(generics.CreateAPIView):
    serializer_class = serializers.SetupIntentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return djstripe_models.SetupIntent.objects.filter(customer__subscriber=self.request.profile)
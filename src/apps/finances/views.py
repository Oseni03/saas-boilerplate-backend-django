from rest_framework import generics, permissions, status
from djstripe import models as djstripe_models

from .services import subscriptions

from . import serializers


class ChangeActiveSubscriptionView(generics.UpdateAPIView):
    serializer_class = serializers.TenantSubscriptionScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return subscriptions.get_schedule(profile=self.request.profile)


class CancelActiveSubscriptionView(generics.UpdateAPIView):
    serializer_class = serializers.CancelTenantActiveSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return subscriptions.get_schedule(profile=self.request.profile)


class PaymentMethodView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.PaymentMethodSerializer
    
    def get_queryset(self):
        return djstripe_models.PaymentMethod.objects.filter("customer__subscriber"==self.request.profile)


class CreatePaymentIntentView(generics.CreateAPIView):
    serializer_class = serializers.PaymentIntentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return djstripe_models.PaymentIntent.objects.filter("customer__subscriber"==self.request.profile)


class UpdatePaymentIntentView(generics.UpdateAPIView):
    serializer_class = serializers.PaymentIntentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return djstripe_models.PaymentIntent.objects.filter("customer__subscriber"==self.request.profile)


class CreateSetupIntentView(generics.CreateAPIView):
    serializer_class = serializers.SetupIntentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return djstripe_models.SetupIntent.objects.filter("customer__subscriber"==self.request.profile)
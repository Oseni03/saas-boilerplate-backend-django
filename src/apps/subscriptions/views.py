from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from . import serializers, models

# Create your views here.
class PricingView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.SubscriptionPriceSerializer


class CreateUserSubscriptionView(generics.CreateAPIView):
    serializer_class = serializers.UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]


class RetrieveUserSubscriptionView(generics.RetrieveAPIView):
    serializer_class = serializers.UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(models.UserSubscription, user=self.request.user)


class UpdateUserSubscriptionView(generics.UpdateAPIView):
    serializer_class = serializers.UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(models.UserSubscription, user=self.request.user)


class CancelUserSubscriptionView(generics.DestroyAPIView):
    serializer_class = serializers.UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(models.UserSubscription, user=self.request.user)


class ListPaymentMethodView(generics.ListAPIView):
    serializer_class = serializers.PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
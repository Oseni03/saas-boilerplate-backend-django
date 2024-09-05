from rest_framework import generics, permissions

from . import serializers, models

# Create your views here.
class PricingView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.SubscriptionPriceSerializer
    queryset = models.SubscriptionPrice.objects.filter(active=True)
    filterset_fields = ("interval",)


class CreateCheckoutView(generics.CreateAPIView):
    serializer_class = serializers.CreateCheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]


class FinalizeCheckoutView(generics.CreateAPIView):
    serializer_class = serializers.UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]


class RetrieveUserSubscriptionView(generics.RetrieveAPIView):
    serializer_class = serializers.UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_sub_obj, _ = models.UserSubscription.objects.get_or_create(user=self.request.user)
        return user_sub_obj


class CancelUserSubscriptionView(generics.UpdateAPIView):
    serializer_class = serializers.CancelActiveUserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_sub_obj, _ = models.UserSubscription.objects.get_or_create(user=self.request.user)
        return user_sub_obj


class CustomerPortalView(generics.CreateAPIView):
    serializer_class = serializers.CustomerPortalSerializer
    permission_classes = [permissions.IsAuthenticated]


class StripeWebhookView(generics.CreateAPIView):
    serializer_class = serializers.WebhookSerializer
    permission_classes = [permissions.AllowAny]
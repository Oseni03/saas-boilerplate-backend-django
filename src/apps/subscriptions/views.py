from rest_framework import generics, permissions, status
from rest_framework.response import Response

from . import serializers, models

# Create your views here.
class PricingView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.SubscriptionPriceSerializer
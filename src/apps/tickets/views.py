from rest_framework import generics, permissions
from .serializers import FeedbackSerializer, SupportSerializer


class FeedbackView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]


class SupportView(generics.CreateAPIView):
    serializer_class = SupportSerializer
    permission_classes = [permissions.AllowAny]

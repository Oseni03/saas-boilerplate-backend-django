from rest_framework import generics, permissions
from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

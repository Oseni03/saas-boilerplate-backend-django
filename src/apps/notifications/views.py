from django.conf import settings
from rest_framework.response import Response
from rest_framework import status, permissions, generics, views

from . import models, serializers, services


class ListNotificationView(generics.ListAPIView):
    model = models.Notification
    serializer_class = serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Notification.objects.filter_by_user(
            self.request.user
        ).order_by('-created_at')


class UpdateNotificationView(generics.UpdateAPIView):
    model = models.Notification
    serializer_class = serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = 'pk'
    lookup_url_kwarg = None
    
    def get_queryset(self):
        return models.Notification.objects.filter_by_user(self.request.user)


class MarkReadAllNotificationsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.NotificationSerializer

    def get(self, request, *args, **kwargs):
        services.NotificationService.mark_read_all_user_notifications(user=request.user)
        return Response({"ok": True}, status=status.HTTP_200_OK)


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = models.NotificationPreference.objects.get_or_create(user=self.request.user)
        return obj
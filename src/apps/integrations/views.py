from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Thirdparty, Integrations
from .serializers import (
    ThirdpartySerializer,
    IntegrationSerializer,
    CreateIntegrationSerializer,
)


# Create your views here.
class ThirdpartyListView(generics.ListAPIView):
    queryset = Thirdparty.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ThirdpartySerializer


class IntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateIntegrationSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return Integrations.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        integration = self.get_object()
        if not integration.is_active:
            return Response(
                {"detail": "Integration is already deactivated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark the integration as inactive
        integration.is_active = False
        integration.save()
        return Response(
            {"detail": "Integration deactivated successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        integration = self.get_object()
        if integration.is_active:
            return Response(
                {"detail": "Integration is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if integration.access_revoked or not integration.access_token:
            pass

        # Reactivate the integration
        integration.is_active = True
        integration.save()
        return Response(
            {"detail": "Integration activated successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        integration = self.get_object()
        if not integration.access_token:
            return Response(
                {"detail": "No access token available to revoke."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Revoke token
        success = integration.revoke_access_token()
        if success:
            integration.access_token = None
            integration.is_active = False
            integration.access_revoked = True
            integration.save()
            return Response(
                {"detail": "Access token revoked and integration deactivated."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "Failed to revoke access token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

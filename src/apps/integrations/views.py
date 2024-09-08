from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Thirdparty, Integration
from .serializers import ThirdpartySerializer, IntegrationSerializer


class ThirdpartyListView(generics.ListAPIView):
    queryset = Thirdparty.objects.filter(is_active=True)
    serializer_class = ThirdpartySerializer
    permission_classes = [IsAuthenticated]


class IntegrationCreateView(generics.CreateAPIView):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.data)
        return super().post(request, *args, **kwargs)


class IntegrationDeactivateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        """
        Deactivate the user's integration for a thirdparty, 
        either using the thirdparty's slug or ID.
        """
        thirdparty = get_object_or_404(Thirdparty, slug=slug)

        # Get the integration between the user and the thirdparty
        try:
            integration = Integration.objects.get(thirdparty=thirdparty, user=request.user, is_active=True)
            integration.is_active = False
            integration.revoke_access_token()  # Revoke the token upon deactivation
            integration.save()
            return Response({"message": "Integration deactivated"}, status=status.HTTP_200_OK)
        except Integration.DoesNotExist:
            return Response(
                {"error": "Integration not found or already inactive"},
                status=status.HTTP_404_NOT_FOUND
            )
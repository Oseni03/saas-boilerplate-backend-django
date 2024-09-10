from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from requests_oauthlib import OAuth2Session
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Thirdparty, Integration
from .serializers import (
    ThirdpartySerializer,
    IntegrationSerializer,
    OAuthCallbackSerializer,
)


class ThirdpartyListView(generics.ListAPIView):
    queryset = Thirdparty.objects.filter(is_active=True)
    serializer_class = ThirdpartySerializer
    permission_classes = [IsAuthenticated]


class IntegrationActivation(APIView):
    def post(self, request, slug, **kwargs):
        try:
            redirect_uri = settings.INTEGRATION_REDIRECT_URL
            platform = Thirdparty.objects.get(slug=slug)
            oauth = OAuth2Session(
                client_id=platform.client_ID,
                redirect_uri=redirect_uri,
                scope=platform.scopes.split(","),
            )  # Assumes scopes are stored as a comma-separated string

            authorization_url, state = oauth.authorization_url(platform.auth_url)

            # Optionally, save `state` if you need to verify it later
            request.session["oauth_state"] = state
            request.session["thirdparty_slug"] = slug

            return Response(
                {"oauth_url": authorization_url}, status=status.HTTP_201_CREATED
            )
        except Thirdparty.DoesNotExist:
            return Response({"error": "Platform not found"}, status=404)


class IntegrationOAuthCallback(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OAuthCallbackSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(
            raise_exception=True
        )  # Using raise_exception=True ensures validation is strict

        state = serializer.validated_data["state"]
        code = serializer.validated_data["code"]

        if state != request.session.get("oauth_state"):
            return Response(
                {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve slug and platform data from session
        slug = request.session.get("thirdparty_slug")
        if not slug:
            return Response({"error": "Session has expired or is invalid"}, status=400)

        try:
            thirdparty = Thirdparty.objects.get(slug=slug)
        except Thirdparty.DoesNotExist:
            return Response({"error": "Platform not found"}, status=404)

        try:
            # Exchange authorization code for tokens
            token = thirdparty.handle_oauth_callback(code)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=400
            )  # Handle token exchange failure

        # Use update_or_create for atomic operations
        Integration.objects.update_or_create(
            user=request.user,
            thirdparty=thirdparty,
            defaults={
                "access_token": token["access_token"],
                "refresh_token": token.get("refresh_token", ""),
                "id_token": token.get("id_token", ""),
                "expires_at": timezone.now() + timedelta(seconds=token["expires_in"]),
            },
        )

        return Response({"message": "Integration successful"})


class IntegrationDeactivateView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IntegrationSerializer

    def get_queryset(self):
        return Integration.objects.filter(user=self.request.user)

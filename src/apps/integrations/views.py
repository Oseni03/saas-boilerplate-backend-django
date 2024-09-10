from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from requests_oauthlib import OAuth2Session
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

            authorization_url, state = oauth.authorization_url(
                platform.auth_url
            )

            # Optionally, save `state` if you need to verify it later
            request.session["oauth_state"] = state
            request.session["thirdparty_slug"] = slug

            return Response({"oauth_url": authorization_url}, status=status.HTTP_201_CREATED)
        except Thirdparty.DoesNotExist:
            return Response({"error": "Platform not found"}, status=404)


class IntegrationOAuthCallback(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        try:
            redirect_uri = settings.INTEGRATION_REDIRECT_URL
            slug = request.session["thirdparty_slug"]
            thirdparty = Thirdparty.objects.get(slug=slug)
            oauth = OAuth2Session(
                client_id=thirdparty.client_ID,
                redirect_uri=redirect_uri,
                state=request.session["oauth_state"],
            )

            # Exchange the authorization code for tokens
            token = oauth.fetch_token(
                thirdparty.token_uri,
                authorization_response=request.build_absolute_uri(),
                client_secret=thirdparty.client_secret,
            )

            # Save tokens to the database
            user_integration, created = Integration.objects.get_or_create(
                user=request.user,
                thirdparty=thirdparty,
                defaults={
                    "access_token": token["access_token"],
                    "refresh_token": token.get("refresh_token"),
                    "expires_at": token["expires_at"],
                },
            )

            if not created:
                # Update the token if the integration already exists
                user_integration.access_token = token["access_token"]
                user_integration.refresh_token = token.get("refresh_token")
                user_integration.expires_at = token["expires_at"]
                user_integration.save()

            return Response({"message": "Integration successful"})
        except Thirdparty.DoesNotExist:
            return Response({"error": "Platform not found"}, status=404)


class IntegrationDeactivateView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IntegrationSerializer

    def get_queryset(self):
        return Integration.objects.filter(user=self.request.user)

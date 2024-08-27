from django.conf import settings
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt import views as jwt_views, tokens as jwt_tokens
from rest_framework_simplejwt.views import TokenViewBase
from djoser.social.views import ProviderAuthView

from common import ratelimit

from .models import UserProfile

from . import serializers, utils, signals, models


class CurrentUserView(generics.GenericAPIView):
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        serializer = self.get_serializer(profile, data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        signals.account_deactivated_signal.send(models.User, instance=request.user)
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = serializers.UserAccountChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # utils.reset_auth_cookie(response)
            return response

        serializer.save()
        response = Response(serializer.data, status=status.HTTP_200_OK)

        utils.set_auth_cookie(
            response,
            {
                settings.AUTH_ACCESS_COOKIE: serializer.data.get("access"),
                settings.AUTH_REFRESH_COOKIE: serializer.data.get("refresh"),
            },
        )
        return response


class CookieTokenObtainView(jwt_views.TokenObtainPairView):
    serializer_class = serializers.CookieTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            response = Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            utils.reset_auth_cookie(response)
            return response

        response = Response(serializer.data, status=status.HTTP_200_OK)

        print(response)

        if serializer.data.get("otp_auth_token"):

            utils.set_auth_cookie(
                response,
                {
                    settings.OTP_AUTH_TOKEN_COOKIE: serializer.data.get("otp_auth_token"),
                },
            )
        else:
            utils.set_auth_cookie(
                response,
                {
                    settings.AUTH_ACCESS_COOKIE: serializer.data.get("access"),
                    settings.AUTH_REFRESH_COOKIE: serializer.data.get("refresh"),
                },
            )
        return response


class SignUpView(generics.GenericAPIView):
    serializer_class = serializers.UserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            utils.reset_auth_cookie(response)
            return response

        serializer.save()
        response = Response(serializer.data, status=status.HTTP_200_OK)

        utils.set_auth_cookie(
            response,
            {
                settings.AUTH_ACCESS_COOKIE: serializer.data.get("access"),
                settings.AUTH_REFRESH_COOKIE: serializer.data.get("refresh"),
            },
        )
        return response


class ConfirmEmailView(generics.GenericAPIView):
    serializer_class = serializers.UserAccountConfirmationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=kwargs)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = serializers.PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    # @ratelimit.ratelimit(key="ip", rate=ratelimit.ip_throttle_rate)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = serializers.PasswordResetConfirmationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        kwargs["new_password"] = request.data.get("new_password")
        serializer = self.get_serializer(data=kwargs)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateOTPView(generics.GenericAPIView):
    serializer_class = serializers.GenerateOTPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = serializers.VerifyOTPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateOTPView(generics.GenericAPIView):
    serializer_class = serializers.ValidateOTPSerializer
    permission_classes = [permissions.AllowAny]

    @ratelimit.ratelimit(key="ip", rate=ratelimit.ip_throttle_rate)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            response.delete_cookie(settings.OTP_AUTH_TOKEN_COOKIE)
            return response

        serializer.save()
        response = Response(serializer.data, status=status.HTTP_200_OK)

        utils.set_auth_cookie(
            response,
            {
                settings.AUTH_ACCESS_COOKIE: serializer.data.get("access"),
                settings.AUTH_REFRESH_COOKIE: serializer.data.get("refresh"),
            },
        )
        return response


class DisableOTPView(generics.GenericAPIView):
    serializer_class = serializers.DisableOTPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenVerifyView(jwt_views.TokenVerifyView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get(settings.AUTH_ACCESS_COOKIE)
        print(access_token)

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)


class CookieTokenRefreshView(jwt_views.TokenRefreshView):
    """Use the refresh token from an HTTP-only cookie and generate new pair (access, refresh)

    post:
    This endpoint is implemented with normal non-GraphQL request because it needs access to a refresh token cookie,
    which is an HTTP-only cookie with a path property set; this means the cookie is never sent to the GraphQL
    endpoint, thus preventing us from adding it to a blacklist.
    """

    serializer_class = serializers.CookieTokenRefreshSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            response = Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
            utils.reset_auth_cookie(response)
            return response

        serializer.save()
        response = Response(serializer.data, status=status.HTTP_200_OK)

        utils.set_auth_cookie(
            response,
            {
                settings.AUTH_ACCESS_COOKIE: serializer.data.get("access"),
                settings.AUTH_REFRESH_COOKIE: serializer.data.get("refresh"),
            },
        )
        return response


class LogoutView(TokenViewBase):
    """Clear cookies containing auth cookies and add refresh token to a blacklist.

    post:
    Logout is implemented with normal non-GraphQL request because it needs access to a refresh token cookie,
    which is an HTTP-only cookie with a path property set; this means the cookie is never sent to the GraphQL
    endpoint, thus preventing us from adding it to a blacklist.
    """

    permission_classes = ()
    serializer_class = serializers.LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        else:
            response = Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        utils.reset_auth_cookie(response)
        return response


class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            utils.set_auth_cookie(
                response,
                {
                    settings.AUTH_ACCESS_COOKIE: access_token,
                    settings.AUTH_REFRESH_COOKIE: refresh_token,
                },
            )

        return response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from apps.users.serializers import UserResponseSerializer
from apps.users.models import CustomUser
from .serializers import (
    RegisterRequestSerializer,
    LoginRequestSerializer,
    TokenPairSerializer,
    VerifyEmailSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
import pyotp
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate email verification token
            token = get_random_string(length=32)
            user.email_verification_token = token
            user.save()

            # Send verification email (placeholder)
            send_mail(
                'Verify your email',
                f'Please verify your email using this token: {token}',
                'no-reply@saas.com',
                [user.email],
            )
            return Response(UserResponseSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if not user.is_verified:
                    return Response({'detail': 'Email not verified'}, status=status.HTTP_403_FORBIDDEN)
                if not user.is_active:
                    return Response({'detail': 'Account is inactive'}, status=status.HTTP_403_FORBIDDEN)

                # Check for MFA
                if user.mfa_enabled:
                    # Generate MFA token (placeholder)
                    mfa_token = get_random_string(length=6, allowed_chars='0123456789')
                    # Send MFA token via email (placeholder)
                    send_mail(
                        'Your MFA Code',
                        f'Your MFA code is: {mfa_token}',
                        'no-reply@saas.com',
                        [user.email],
                    )
                    return Response({'detail': 'MFA code sent'}, status=status.HTTP_200_OK)
                else:
                    # Generate token pair
                    refresh_token = RefreshToken.for_user(user)
                    return Response(TokenPairSerializer(refresh_token).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                serializer = TokenPairSerializer({'access_token': new_access_token, 'refresh_token': str(refresh)})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Token refresh error: {str(e)}")
                return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            # Placeholder for token verification logic
            try:
                user = CustomUser.objects.get(email_verification_token=token)
                user.is_verified = True
                user.email_verification_token = ''
                user.save()
                return Response(UserResponseSerializer(user).data, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                # Generate password reset token (placeholder)
                token = get_random_string(length=32)
                user.password_reset_token = token
                user.save()
                # Send password reset email (placeholder)
                send_mail(
                    'Password Reset Request',
                    f'Please reset your password using this token: {token}',
                    'no-reply@saas.com',
                    [user.email],
                )
                return Response({'detail': 'Password reset token sent'}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            try:
                user = CustomUser.objects.get(password_reset_token=token)
                user.set_password(new_password)
                user.password_reset_token = ''
                user.save()
                return Response(UserResponseSerializer(user).data, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserResponseSerializer(user).data, status=status.HTTP_200_OK)


class SetupMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        mfa_uri = user.get_mfa_uri()
        return Response({'provisioning_uri': mfa_uri, 'secret': user.mfa_secret}, status=status.HTTP_200_OK)


class VerifyMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.query_params.get('code')
        if not code:
            return Response({'detail': 'Code required'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.mfa_secret:
            return Response({'detail': 'MFA not set up'}, status=status.HTTP_400_BAD_REQUEST)
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code):
            user.mfa_enabled = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)


class DisableMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'detail': 'Code required'}, status=status.HTTP_400_BAD_REQUEST)
        totp = pyotp.TOTP(request.user.mfa_secret)
        if totp.verify(code):
            request.user.mfa_enabled = False
            request.user.mfa_secret = ''
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)


class ValidateMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'detail': 'Code required'}, status=status.HTTP_400_BAD_REQUEST)
        totp = pyotp.TOTP(request.user.mfa_secret)
        if totp.verify(code):
            refresh = RefreshToken.for_user(request.user)
            serializer = TokenPairSerializer({'access_token': str(refresh.access_token), 'refresh_token': str(refresh)})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    RefreshView,
    VerifyEmailView,
    ForgotPasswordView,
    ResetPasswordView,
    GetMeView,
    SetupMFAView,
    VerifyMFAView,
    DisableMFAView,
    ValidateMFAView,
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("refresh", RefreshView.as_view(), name="token_refresh"),
    path("verify-email", VerifyEmailView.as_view(), name="verify_email"),
    path("forgot-password", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password", ResetPasswordView.as_view(), name="reset_password"),
    path("me", GetMeView.as_view(), name="get_me"),
    # path("oauth/google")
    # path("oauth/google/callback")
    path("mfa/setup", SetupMFAView.as_view(), name="setup_mfa"),
    path("mfa/verify", VerifyMFAView.as_view(), name="verify_mfa"),
    path("mfa/disable", DisableMFAView.as_view(), name="disable_mfa"),
    path("mfa/validate", ValidateMFAView.as_view(), name="validate_mfa"),
]
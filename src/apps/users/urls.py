from django.conf import settings
from django.urls import path, include, re_path
from social_core.utils import setting_name

extra = getattr(settings, setting_name("TRAILING_SLASH"), True) and "/" or ""

from . import views

social_patterns = [
    # authentication / association
    re_path(
        r'^o/(?P<provider>\S+)/$',
        views.CustomProviderAuthView.as_view(),
        name='provider-auth'
    ),
]

auth_patterns = [
    path('jwt/verify/', views.CustomTokenVerifyView.as_view(), name="jwt_token_verify"),
    path("jwt/refresh/", views.CookieTokenRefreshView.as_view(), name="jwt_token_refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("login/", views.CookieTokenObtainView.as_view(), name="login"),
    path("register/", views.SignUpView.as_view(), name="register"),
    path("activate/<str:user>/<token>/", views.ConfirmEmailView.as_view(), name="confirm-email"),
    path("password-reset/", views.PasswordResetView.as_view(), name="password-reset"),
    path("password-reset/confirm/<str:user>/<token>/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("validate-otp/", views.ValidateOTPView.as_view(), name="validate-otp"),
    path('social/', include((social_patterns, 'social'), namespace='social')),
]

user_patterns = [
    path("me/", views.CurrentUserView.as_view(), name="profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("generate-otp/", views.GenerateOTPView.as_view(), name="generate-otp"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify-otp"),
    path("disable-otp/", views.DisableOTPView.as_view(), name="disable-otp"),
]

urlpatterns = [
    path("auth/", include(auth_patterns)),
    path("users/", include(user_patterns)),
]

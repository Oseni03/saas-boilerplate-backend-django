from django.urls import path, include

from apps.users.views import (
    UserProfileView,
    ChangePasswordView
)


urlpatterns = [
    path("me", UserProfileView.as_view(), name="user_profile"),
    path("change-password", ChangePasswordView.as_view(), name="change_password"),
]
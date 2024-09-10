from django.urls import path, re_path
from .views import ThirdpartyListView, IntegrationActivation, IntegrationDeactivateView, IntegrationOAuthCallback

urlpatterns = [
    path("thirdparty/", ThirdpartyListView.as_view(), name="thirdparty-list"),
    path(
        "activate/<slug:slug>/",
        IntegrationActivation.as_view(),
        name="integration-activate",
    ),
    path("callback/", IntegrationOAuthCallback.as_view(), name="oauth-callback"),
    path(
        "deactivate/<pk>/",
        IntegrationDeactivateView.as_view(),
        name="integration-deactivate",
    ),
]

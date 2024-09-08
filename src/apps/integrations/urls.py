from django.urls import path
from .views import ThirdpartyListView, IntegrationCreateView, IntegrationDeactivateView

urlpatterns = [
    path("thirdparty/", ThirdpartyListView.as_view(), name="thirdparty-list"),
    path("activate/", IntegrationCreateView.as_view(), name="integration-activate"),
    path(
        "deactivate/<slug:slug>/",
        IntegrationDeactivateView.as_view(),
        name="integration-deactivate",
    ),
]

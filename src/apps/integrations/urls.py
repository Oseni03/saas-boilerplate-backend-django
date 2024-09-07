from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet

from . import views

# Set up the router
router = DefaultRouter()
router.register(r"", IntegrationViewSet, basename="integrations")

urlpatterns = [
    path("thirdparties/", views.ThirdpartyListView.as_view(), name="list-thirdparty"),
    path("", include(router.urls)),
]
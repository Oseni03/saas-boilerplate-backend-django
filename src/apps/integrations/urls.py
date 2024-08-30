from django.urls import path, include

from . import views


urlpatterns = [
    path("thirdparties/", views.ThirdpartyListView.as_view(), name="list-thirdparty"),
    path("", views.IntegrationView.as_view(), name="integration"),
]
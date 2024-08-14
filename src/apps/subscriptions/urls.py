from django.urls import path, include

from . import views


pricing_urlpatterns = [
    path("", views.PricingView.as_view()),
]

urlpatterns = [
    path("pricing/", include(pricing_urlpatterns)),
]
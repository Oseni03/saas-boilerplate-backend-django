from django.urls import path, include

from . import views


pricing_urlpatterns = [
    path("", views.PricingView.as_view()),
]

subscriptions_urlpatterns = [
    path("create/", views.CreateUserSubscriptionView.as_view()),
    path("update/", views.UpdateUserSubscriptionView.as_view()),
    path("payment-methods/", views.ListPaymentMethodView.as_view()),
    path("", views.RetrieveUserSubscriptionView.as_view()),
]

urlpatterns = [
    path("pricing/", include(pricing_urlpatterns)),
    path("subscriptions/", include(subscriptions_urlpatterns)),
]
from django.urls import path, include

from . import views


stripe_urls = [
    path("", include("djstripe.urls", namespace="djstripe")),
]

urlpatterns = [
    path("change-subscription/", views.ChangeActiveSubscriptionView.as_view(), name="change-active-subscription"),
    path("cancel-subscription/", views.CancelActiveSubscriptionView.as_view(), name="cancel-active-subscription"),
    path("payment-method/<pk>", views.PaymentMethodView.as_view(), name="payment-method"),
    path("create-payment-intent/", views.CreatePaymentIntentView.as_view(), name="create-payment-intent"),
    path("update-payment-intent/<pk>", views.UpdatePaymentIntentView.as_view(), name="update-payment-intent"),
    path("setup-intent/", views.CreateSetupIntentView.as_view(), name="create-setup-intent"),
    path("stripe/", include(stripe_urls)),
]

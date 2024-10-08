from django.urls import path, include

from . import views


pricing_urlpatterns = [
    path("", views.PricingView.as_view()),
]

subscriptions_urlpatterns = [
    path("create-checkout/", views.CreateCheckoutView.as_view()),
    path("finalize-checkout/", views.FinalizeCheckoutView.as_view()),
    path("cancel/", views.CancelUserSubscriptionView.as_view()),
    path("create-customer-portal/", views.CustomerPortalView.as_view()),
    path("", views.RetrieveUserSubscriptionView.as_view()),
]

urlpatterns = [
    path("pricing/", include(pricing_urlpatterns)),
    path("subscriptions/", include(subscriptions_urlpatterns)),
    path("webhook/", views.StripeWebhookView.as_view()),
]
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.ListNotificationView.as_view(), name="notification-list"),
    path("<pk>/update/", views.UpdateNotificationView.as_view(), name="notification-update"),
    path("mark-read/", views.MarkReadAllNotificationsView.as_view(), name="notification-mark-read"),
    path("preferences/", views.NotificationPreferenceView.as_view(), name="notification-preferences"),
]
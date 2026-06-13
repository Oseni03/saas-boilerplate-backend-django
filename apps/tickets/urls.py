from django.urls import path 

from . import views


urlpatterns = [
    path("feedbacks/", views.FeedbackView.as_view(), name="create-feedback"),
    path("supports/", views.SupportView.as_view(), name="create-support"),
]
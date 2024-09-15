from django.urls import path
from .views import TaskResultView

urlpatterns = [
    path('execute-task/', TaskResultView.as_view(), name='execute-task'),
]

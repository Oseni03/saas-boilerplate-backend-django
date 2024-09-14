from django.urls import path
from .views import execute_task

urlpatterns = [
    path('execute-task/', execute_task, name='execute-task'),
]

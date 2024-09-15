from django.conf import settings

from apps.aws_tasks.utils import lambda_task
from .models import Subscription


@lambda_task
def user_sub_post_save_task(instance):
    


@lambda_task
def user_sub_post_delete_task(instance):
    
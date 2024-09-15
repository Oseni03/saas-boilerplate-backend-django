from django.dispatch import Signal

from apps.aws_tasks.utils import get_task_name, send_task_to_sqs
from .models import User
from .tasks import deactivate_user_account_task, send_account_confirmation_email_task

email_confirmed_signal = Signal()
send_account_confirmation_email_signal = Signal()
account_deactivated_signal = Signal()


def send_account_confirmation_email(sender, instance, *args, **kwargs):
    task_name = get_task_name(send_account_confirmation_email_task)
    send_task_to_sqs(task_name=task_name, instance=instance)


send_account_confirmation_email_signal.connect(
    send_account_confirmation_email, sender=User
)


def deactivate_user_account(sender, instance, *args, **kwargs):
    task_name = get_task_name(deactivate_user_account_task)
    send_task_to_sqs(task_name=task_name, instance=instance)


account_deactivated_signal.connect(deactivate_user_account, sender=User)

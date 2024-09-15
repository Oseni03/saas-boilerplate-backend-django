import boto3
import json
from functools import wraps
from django.conf import settings
from django.core.cache import cache

from .models import TaskResult, StateChoice

sqs = None
try:
    sqs = boto3.client("sqs", region_name=settings.AWS_REGION)
except Exception as e:
    if sqs is None and settings.ENABLE_AWS_LAMBDA:
        raise e


def get_task_name(func):
    return f"{func.__module__}.{func.__name__}"


def lambda_task(func):
    """
    Decorator to register a task and sync its logic with AWS Lambda.
    """
    task_name = get_task_name(func)

    # Register the task in the cache
    cache_key = f"task_{task_name}"
    cache.set(cache_key, func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the actual function
        try:
            task = TaskResult.objects.get(task_name=task_name)
            task.status = StateChoice.STARTED
            task.save()

            # Execute the task
            result = func(*args, **kwargs)

            # Mark task as SUCCESS and save result in the database
            task.status = StateChoice.SUCCESS
            task.result = str(result)
            task.save()
        except Exception as e:
            task.status = StateChoice.FAILURE
            task.traceback = str(e)
            task.save()
            raise e

        return result

    return wrapper


def send_task_to_sqs(task_name, delay_seconds=0, *args, **kwargs):
    """
    Sends a task to AWS SQS for execution after a delay.
    """
    task_data = {
        "task": task_name,
        "args": args,
        "kwargs": kwargs,
    }
    TaskResult.objects.create(task_name=task_name, task_args=args, task_kwargs=kwargs)
    sqs.send_message(
        QueueUrl=settings.AWS_SQS_QUEUE_URL,
        MessageBody=json.dumps(task_data),
        DelaySeconds=delay_seconds,  # Delay in seconds (max: 15 minutes or 900 seconds
    )


def process_task(task_name, *args, **kwargs):
    cache_key = f"task_{task_name}"
    task_func = cache.get(cache_key)

    if task_func:
        return task_func(*args, **kwargs)
    else:
        raise Exception(f"Task '{task_name}' not found in cache")

from django.http import JsonResponse
from django.core.cache import cache
import json

from apps.aws_tasks.models import StateChoice, TaskResult


def execute_task(request):
    """
    View to execute the task received from AWS Lambda.
    """
    task_name = request.POST.get("task_name")
    args = json.loads(request.POST.get("args", "[]"))
    kwargs = json.loads(request.POST.get("kwargs", "{}"))

    # Retrieve the task function from the cache
    cache_key = f"task_{task_name}"
    task_func = cache.get(cache_key)

    if task_func:
        task = TaskResult.objects.get(task_name=task_name)
        task.status = StateChoice.STARTED
        task.save()
        try:
            # Execute the task
            result = task_func(*args, **kwargs)

            task.status = StateChoice.SUCCESS
            task.result = str(result)
            task.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            task.status = StateChoice.FAILURE
            task.traceback = str(e)
            task.save()
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse(
            {"status": "error", "message": "Task not found"}, status=404
        )

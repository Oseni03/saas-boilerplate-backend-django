from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response

from apps.aws_tasks.models import StateChoice, TaskResult
from .serializers import TaskSerializer


class TaskResultView(generics.GenericAPIView):
    serializer_class = TaskSerializer

    def post(self, request, *args, **kwargs):
        """
        View to execute the task received from AWS Lambda.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_name = serializer.validated_data.get("task_name")
        args = serializer.validated_data.get("args", "[]")
        kwargs = serializer.validated_data.get("kwargs", "{}")

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
                return Response({"status": "success"}, status=status.HTTP_200_OK)
            except Exception as e:
                task.status = StateChoice.FAILURE
                task.traceback = str(e)
                task.save()
                return Response(
                    {"status": "error", "message": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"status": "error", "message": "Task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

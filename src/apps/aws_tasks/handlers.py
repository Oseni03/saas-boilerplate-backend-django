import json
import boto3
import requests
from django.conf import settings

def lambda_handler(event, context):
    for record in event['Records']:
        task_data = json.loads(record['body'])
        task_name = task_data.get('task')
        args = task_data.get('args', [])
        kwargs = task_data.get('kwargs', {})

        # Invoke the task by making an HTTP request to the Django app
        response = requests.post(
            f'{settings.BACKEND_DOMAIN_URL}/execute-task/',
            data={
                'task_name': task_name,
                'args': json.dumps(args),
                'kwargs': json.dumps(kwargs)
            }
        )

        # Check the response
        if response.status_code == 200:
            print(f"Successfully executed task {task_name}")
        else:
            print(f"Failed to execute task {task_name}, response: {response.content}")

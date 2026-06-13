import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Notification
from .serializers import NotificationSerializer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the user ID from the scope
        self.user_id = str(self.scope['user'].id)

        # Create a unique group name for the user based on their ID
        self.group_name = self.user_id

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when the WebSocket disconnects
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # This method handles incoming WebSocket messages from the client
        text_data_json = json.loads(text_data)

        print(text_data_json)
        # Assuming the payload contains an 'id' to fetch the notification
        notification_id = text_data_json.get('id')

        if notification_id:
            notification_data = await self.get_notification(notification_id)
            if notification_data:
                await self.send(text_data=json.dumps({
                    'notification': notification_data
                }))

    @sync_to_async
    def get_notification(self, id: str):
        try:
            # Fetch the notification and serialize it
            notification = Notification.objects.prefetch_related('issuer', 'issuer__profile').get(id=id)
            serializer = NotificationSerializer(notification)
            return serializer.data
        except Notification.DoesNotExist:
            return None

    async def notify(self, event):
        # Send the notification to the WebSocket
        notification_data = event['notification']
        await self.send(text_data=json.dumps({
            'notification': notification_data
        }))

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for handling real-time notifications via WebSocket.
    """

    async def connect(self):
        # Assign the user-specific group name
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()

        self.group_name = f"notifications_{self.user.id}"

        # Add the user to their notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the notification group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        """
        Handle sending notifications over WebSocket.
        """
        # Send the notification to the WebSocket
        await self.send(text_data=json.dumps(event["message"]))
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for handling real-time notifications via WebSocket.
    """

    async def connect(self):
        """
        Handles a new WebSocket connection from the client.
        """
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            logger.info(f"User not authenticated: {self.user}")
            await self.close()
            return
        
        if self.user.is_anonymous:
            await self.close()
            return

        self.group_name = f"notifications_{self.user.id}"

        # Add the user to their notification group
        try:
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            logger.info(f"User {self.user} added to group {self.group_name}")
        except Exception as e:
            logger.error(
                f"Error adding user {self.user} to group: {e}", exc_info=True
            )
            await self.close()

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnections.
        """
        try:
            # Remove the user from the notification group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"User {self.user} removed from group {self.group_name}")
        except Exception as e:
            logger.error(
                f"Error removing user {self.user} from group: {e}", exc_info=True
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages from the WebSocket.
        """
        try:
            data = json.loads(text_data)
            if data.get("type") == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
        except Exception:
            pass

    async def send_notification(self, event):
        """
        Handles sending notifications over WebSocket.
        """
        message = event.get("message")

        if not message:
            logger.warning("Received event with no message.")
            return

        # Send the notification to the WebSocket
        try:
            await self.send(text_data=json.dumps(message))
            logger.info(f"Notification sent to {self.user}")
        except Exception as e:
            logger.error(
                f"Error sending notification to {self.user}: {e}", exc_info=True
            )


    async def receive_json(self, content, **kwargs):
        # Optional: Handle client-sent messages
        pass

    async def notify(self, event):
        await self.send_json(event["data"])
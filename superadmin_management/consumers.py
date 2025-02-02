import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class SuperadminNotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time Superadmin notifications."""

    async def connect(self):
        """Connects the WebSocket and joins the 'superadmin_notifications' group."""
        if self.scope["user"].is_authenticated and self.scope["user"].role == "superadmin":
            await self.channel_layer.group_add("superadmin_notifications", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Removes the connection from the notifications group."""
        await self.channel_layer.group_discard("superadmin_notifications", self.channel_name)

    async def receive_json(self, content):
        """Handles incoming messages (if needed)."""
        pass

    async def send_notification(self, event):
        """Sends a notification to connected Superadmins."""
        await self.send(text_data=json.dumps(event["message"]))



class LogNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("superadmin_notifications", self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({"message": "Received"}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("superadmin_notifications", self.channel_name)

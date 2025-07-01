from channels.generic.websocket import AsyncWebsocketConsumer
import json
from communications.services.presence_service import PresenceService

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f"chat_{self.thread_id}"

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Add to presence
        await PresenceService.add_user(self.thread_id, self.user.id, self.user.username)

        # Broadcast presence update
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast.joined",
                "user_id": self.user.id,
                "username": self.user.username
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

        # Remove from presence
        await PresenceService.remove_user(
            self.thread_id, self.user.id
        )

        # Broadcast presence update
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast.left",
                "user_id": self.user.id,
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data['message'],
                'sender': data['sender'],
                'timestamp': data.get('timestamp')
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


    async def broadcast_joined(self, event):
        await self.send_json({
            "type": "presence_joined",
            "user_id": event["user_id"],
            "username": event["username"]
        })

    async def broadcast_left(self, event):
        await self.send_json({
            "type": "presence_left",
            "user_id": event["user_id"],
        })

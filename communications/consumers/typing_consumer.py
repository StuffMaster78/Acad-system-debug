from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TypingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.group_name = f"typing_{self.thread_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "typing_status",
                "user_id": data["user_id"],
                "is_typing": data["is_typing"]
            }
        )

    async def typing_status(self, event):
        await self.send(text_data=json.dumps(event))
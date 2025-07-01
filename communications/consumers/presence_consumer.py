from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.group_name = f"presence_{self.thread_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.group_name, {
            "type": "presence_status", "status": "online"
        })

    async def disconnect(self, code):
        await self.channel_layer.group_send(self.group_name, {
            "type": "presence_status", "status": "offline"
        })
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def presence_status(self, event):
        await self.send(text_data=json.dumps(event))
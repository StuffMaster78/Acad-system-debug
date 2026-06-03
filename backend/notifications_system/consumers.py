from __future__ import annotations

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

log = logging.getLogger(__name__)

NOTIFICATIONS_GROUP = "notifications_{user_id}"


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Per-user WebSocket consumer for real-time in-app notifications.

    The frontend connects with a JWT token as a query param:
        ws://.../ws/notifications/?token=<jwt>

    On connect the consumer joins group `notifications_{user_id}`.
    When the backend broadcasts a notification it sends to that group
    and the consumer forwards it as a JSON message to the client.

    The consumer is read-only from the frontend perspective — it only
    receives pushes, it does not process messages sent from the browser.
    """

    async def connect(self):
        user = await self._authenticate()
        if user is None:
            await self.close(code=4001)
            return

        self.user_id = user.pk
        self.group_name = NOTIFICATIONS_GROUP.format(user_id=self.user_id)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        log.debug("NotificationConsumer connected user=%s", self.user_id)

    async def disconnect(self, code):
        group = getattr(self, "group_name", None)
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)
        log.debug("NotificationConsumer disconnected user=%s code=%s", getattr(self, "user_id", "?"), code)

    async def receive(self, text_data=None, bytes_data=None):
        pass  # client never sends — ignore

    async def notification_push(self, event: dict):
        """
        Handler for channel layer messages with type='notification.push'.
        Forwards the payload to the WebSocket client.
        """
        await self.send(text_data=json.dumps(event.get("payload", {})))

    async def _authenticate(self):
        """
        Resolve the authenticated user from the JWT query-string token.
        Returns the User instance or None if unauthenticated.
        """
        from channels.db import database_sync_to_async
        from urllib.parse import parse_qs

        query = parse_qs(self.scope.get("query_string", b"").decode())
        token = (query.get("token") or [None])[0]
        if not token:
            return None

        @database_sync_to_async
        def _resolve(tok):
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                from django.contrib.auth import get_user_model
                User = get_user_model()
                payload = AccessToken(tok)
                return User.objects.get(pk=payload["user_id"])
            except Exception:
                return None

        return await _resolve(token)

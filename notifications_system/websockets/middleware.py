import jwt
import logging
from urllib.parse import parse_qs

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware.base import BaseMiddleware
from django.core.cache import cache
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.settings import api_settings

import datetime
from django.utils.timezone import now

from users.models import User

logger = logging.getLogger(__name__)
class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_seen = request.session.get("last_seen_at")
            now_time = now().isoformat()
            request.session["last_seen_at"] = now_time
        return self.get_response(request)


class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom JWT Auth Middleware for WebSocket connections.
    """
    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]
        scope["user"] = AnonymousUser()

        if token:
            try:
                UntypedToken(token)
                decoded_data = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[api_settings.ALGORITHM]
                )
                user_id = decoded_data.get("user_id")
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                scope["user"] = user
                logger.debug(f"WebSocket authenticated user: {user}")
            except Exception as e:
                logger.warning(f"WebSocket JWT auth failed: {e}")

        return await super().__call__(scope, receive, send)


class RateLimitMiddleware(BaseMiddleware):
    """
    Simple per-IP rate limiter for WebSocket connections.
    """
    async def __call__(self, scope, receive, send):
        ip = self._get_ip(scope)
        path = scope.get("path", "")
        key = f"ws-rate:{ip}:{path}"

        if not await database_sync_to_async(self._check_rate_limit)(key):
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            await send({"type": "websocket.close", "code": 4001})
            return

        return await super().__call__(scope, receive, send)

    def _check_rate_limit(self, key):
        current = cache.get(key, 0)
        if current >= 10:
            return False
        cache.set(key, current + 1, timeout=60)
        return True

    def _get_ip(self, scope):
        headers = dict(scope["headers"])
        xff = headers.get(b"x-forwarded-for")
        return xff.decode().split(",")[0] if xff else scope["client"][0]
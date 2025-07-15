from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter # type: ignore
from notifications_system.consumers import NotificationConsumer
from .middlewares import TokenAuthMiddleware, RateLimitMiddleware # type: ignore

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": RateLimitMiddleware(
        TokenAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
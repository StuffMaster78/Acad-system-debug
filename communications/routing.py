from django.urls import re_path
from .consumers import (
    chat_consumer, typing_consumer, presence_consumer
)

websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<thread_id>[^/]+)/$",
        chat_consumer.ChatConsumer.as_asgi()
    ),
    re_path(
        r"ws/typing/(?P<thread_id>[^/]+)/$",
        typing_consumer.TypingConsumer.as_asgi()
    ),
    re_path(
        r"ws/presence/(?P<thread_id>[^/]+)/$",
        presence_consumer.PresenceConsumer.as_asgi()
    ),
]
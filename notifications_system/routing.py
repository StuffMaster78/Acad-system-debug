from django.urls import path
from .consumers import NotificationConsumer
from django.urls import re_path
from .consumers import SuperadminNotificationConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    re_path(r'ws/superadmin/notifications/$', SuperadminNotificationConsumer.as_asgi()),
]
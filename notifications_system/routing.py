from django.urls import path
from .consumers import NotificationConsumer, SuperadminNotificationConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/superadmin/notifications/", SuperadminNotificationConsumer.as_asgi()),
]
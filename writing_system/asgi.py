"""
ASGI config for writing_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter # type: ignore
from channels.auth import AuthMiddlewareStack # type: ignore
import communications
import communications.routing
import notifications_system.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications_system.routing.websocket_urlpatterns + communications.routing.websocket_urlpatterns
        )
    ),
})


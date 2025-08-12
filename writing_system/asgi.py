"""
ASGI config for writing_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E501
from channels.auth import AuthMiddlewareStack  # noqa: E501
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E501


import communications.routing
import notifications_system.websockets.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')


# Build combined websocket routes
websocket_routes = (
    notifications_system.websockets.routing.websocket_urlpatterns
    + communications.routing.websocket_urlpatterns
)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_routes)
        )
    ),
})


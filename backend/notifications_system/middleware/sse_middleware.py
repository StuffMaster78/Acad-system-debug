from __future__ import annotations

from typing import Callable

from django.conf import settings
from django.contrib.auth.middleware import get_user
from django.http import HttpResponseForbidden
from django.http import HttpRequest, HttpResponse


class SSEAuthMiddleware:
    """Authenticate SSE connections for the notifications stream.

    This middleware ensures that only authenticated users can access the
    Server-Sent Events (SSE) endpoint used for live notifications.

    Configuration:
        Set ``NOTIFICATIONS_SSE_PATH`` in settings to override the path.
        Default is ``/notifications/stream``.

    Order:
        Place this *after* AuthenticationMiddleware in MIDDLEWARE.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.stream_path = getattr(
            settings,
            "NOTIFICATIONS_SSE_PATH",
            "/notifications/stream",
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and enforce auth on the SSE endpoint.

        Returns:
            HttpResponse: 403 for unauthenticated SSE access, otherwise
            passes the request downstream.
        """
        if request.path_info == self.stream_path:
            # Optional: require GET for SSE; most clients use GET.
            if request.method != "GET":
                return HttpResponseForbidden("Method not allowed for SSE.")

            # Optional: enforce Accept header for SSE clients.
            # if "text/event-stream" not in request.headers.get("Accept", ""):
            #     return HttpResponseForbidden("Invalid Accept header.")

            user = get_user(request)
            if not getattr(user, "is_authenticated", False):
                return HttpResponseForbidden(
                    "You are not allowed to access this resource."
                )

        # Always continue the middleware chain.
        return self.get_response(request)
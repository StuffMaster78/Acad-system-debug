"""
Session activity middleware for idle tracking and frontend UX.

This middleware does not log users out or revoke authentication.
It only tracks activity and exposes timing metadata so the frontend
can warn the user or react appropriately.
"""

from django.conf import settings
from django.utils import timezone

from authentication.services.login_session_service import (
    LoginSessionService,
)


class SessionActivityMiddleware:
    """
    Track request activity and expose idle/session timing metadata.

    This middleware is UX-only. Real session validity is enforced
    elsewhere.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.idle_timeout = getattr(
            settings,
            "SESSION_IDLE_TIMEOUT",
            30 * 60,
        )
        self.warning_time = getattr(
            settings,
            "SESSION_WARNING_TIME",
            5 * 60,
        )

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return response

        effective_timeout = self.idle_timeout

        # Prefer real LoginSession data if enforcement middleware attached it
        login_session = getattr(request, "_login_session", None)
        if login_session is not None:
            effective_timeout = (
                LoginSessionService.get_idle_timeout_seconds(
                    session=login_session,
                )
            )
            idle_remaining = (
                LoginSessionService.get_idle_remaining_seconds(
                    session=login_session,
                )
            )
            idle_time = max(effective_timeout - idle_remaining, 0)
        else:
            now_ts = timezone.now().timestamp()
            last_activity = request.session.get("last_activity_ts", now_ts)
            idle_time = max(now_ts - last_activity, 0)
            idle_remaining = max(effective_timeout - idle_time, 0)

            request.session["last_activity_ts"] = now_ts
            request.session.modified = True

        response["X-Session-Idle-Time"] = str(int(idle_time))
        response["X-Session-Remaining"] = str(int(idle_remaining))
        response["X-Session-Timeout"] = str(int(effective_timeout))
        response["X-Session-Warning-Time"] = str(int(self.warning_time))

        return response
"""
Synchronize request activity to LoginSession records when possible.
"""

from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.token_service import TokenService


class LoginSessionActivitySyncMiddleware:
    """
    Update LoginSession.last_activity for authenticated requests when a
    session token can be resolved.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return response

        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return response

        raw_token = auth.removeprefix("Bearer ").strip()
        if not raw_token:
            return response

        try:
            token_hash = TokenService.hash_value(raw_token)
        except Exception:
            return response

        website = getattr(request, "website", None)
        session = LoginSessionService.get_active_session_by_token_hash(
            token_hash=token_hash,
            website=website,
        )

        if session is not None:
            LoginSessionService.touch_session(session=session)

        return response
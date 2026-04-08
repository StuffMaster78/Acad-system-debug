"""
Enforce LoginSession validity for JWT-authenticated requests.
"""
import logging
from django.core.exceptions import PermissionDenied

from authentication.services.login_session_service import (
    LoginSessionService,
)

logger = logging.getLogger(__name__)


class LoginSessionEnforcementMiddleware:
    """
    Ensure that every authenticated request is backed by a valid LoginSession.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = None

        user = getattr(request, "user", None)
        auth = getattr(request, "auth", None)

        # Only apply to authenticated JWT requests
        if user and user.is_authenticated and auth:
            try:
                session_id = self._get_int_claim(auth, "session_id")
                # raw_session_id = self._get_claim(auth, "session_id")
                # session_id: int | None = None

                # if isinstance(raw_session_id, int):
                #     session_id = raw_session_id
                # elif isinstance(raw_session_id, str) and raw_session_id.isdigit():
                #     session_id = int(raw_session_id)

                if session_id is not None:
                    session = LoginSessionService.get_session_by_id(
                        session_id=session_id,
                        user=user,
                        website=getattr(request, "website", None),
                    )

                    if session is None:
                        raise PermissionDenied("Session not found.")
                    
                    was_revoked = LoginSessionService.revoke_if_expired(
                    session=session,
                    )
                    if was_revoked:
                        raise PermissionDenied(
                            "Session has expired or is no longer valid."
                        )

                    if not session.is_active:
                        raise PermissionDenied(
                            "Session is no longer valid."
                        )

                    # THIS IS THE IMPORTANT PART
                    LoginSessionService.touch_session(session=session)

                    # attach for downstream use
                    request._login_session = session

            except PermissionDenied:
                raise
            except Exception as exc:
                # fail closed? or open?
                # safer: fail open but log (your call)
                logger.exception(
                    "Unexpected error during login session enforcement."
                )
                raise PermissionDenied(
                    "Session validation failed."
                ) from exc

        response = self.get_response(request)
        return response

    @staticmethod
    def _get_claim(auth, key):
        if isinstance(auth, dict):
            return auth.get(key)

        getter = getattr(auth, "get", None)
        if callable(getter):
            return getter(key)

        try:
            return auth[key]
        except Exception:
            return None
        
    @staticmethod
    def _get_int_claim(auth, key) -> int | None:
        value = LoginSessionEnforcementMiddleware._get_claim(
            auth,
            key
        )

        if isinstance(value, int):
            return value

        if isinstance(value, str) and value.isdigit():
            return int(value)

        return None
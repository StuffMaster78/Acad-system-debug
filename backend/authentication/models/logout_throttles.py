from rest_framework.throttling import SimpleRateThrottle

from authentication.models.rate_limit_event import RateLimitEvent
from authentication.services.rate_limit_security_bridge import (
    RateLimitSecurityBridgeService,
)
from authentication.utils.ip import get_client_ip


class LogoutAllSessionsThrottle(SimpleRateThrottle):
    """
    Throttle logout-all-sessions requests by authenticated user,
    falling back to IP when needed.
    """

    scope = "logout_all_sessions"

    def get_cache_key(self, request, view):
        self._request_for_logging = request

        website_id = getattr(
            getattr(request, "website", None),
            "pk",
            None,
        ) or getattr(
            getattr(getattr(request, "user", None), "website", None),
            "pk",
            None,
        ) or "global"

        if getattr(request, "user", None) and request.user.is_authenticated:
            return (
                f"throttle:{self.scope}:"
                f"website:{website_id}:user:{request.user.pk}"
            )

        ident = self.get_ident(request)
        return (
            f"throttle:{self.scope}:"
            f"website:{website_id}:ip:{ident}"
        )

    def throttle_failure(self):
        request = getattr(self, "_request_for_logging", None)

        if request is not None:
            RateLimitSecurityBridgeService.record_rate_limit_event(
                user=(
                    request.user
                    if getattr(request, "user", None)
                    and request.user.is_authenticated
                    else None
                ),
                website=getattr(request, "website", None),
                ip_address=get_client_ip(request),
                user_agent=request.headers.get("User-Agent", ""),
                path=request.path,
                method=request.method,
                reason=RateLimitEvent.Reason.UNKNOWN,
            )

        return super().throttle_failure()
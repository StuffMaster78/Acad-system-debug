from rest_framework.throttling import SimpleRateThrottle

from authentication.models.rate_limit_event import RateLimitEvent
from authentication.services.rate_limit_security_bridge import (
    RateLimitSecurityBridgeService
)
from authentication.utils.ip import get_client_ip


class LoginRateThrottle(SimpleRateThrottle):
    """
    Throttle login requests by authenticated user when available,
    otherwise by IP address.
    """

    scope = "login"

    def get_cache_key(self, request, view):
        """
        Build the cache key for login throttling.
        """
        self._request_for_logging = request

        website_id = getattr(
            getattr(request, "website", None),
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
        """
        Log the rate-limit event when throttling occurs.
        """
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
                reason=RateLimitEvent.Reason.LOGIN_THROTTLE,
            )

        return super().throttle_failure()
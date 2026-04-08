from rest_framework.throttling import SimpleRateThrottle

from authentication.models.rate_limit_event import RateLimitEvent
from authentication.services.rate_limit_security_bridge import (
    RateLimitSecurityBridgeService,
)
from authentication.utils.ip import get_client_ip


class LoginRateThrottle(SimpleRateThrottle):
    """
    Throttle login requests by authenticated user when available,
    otherwise by IP address.
    """

    scope = "login"

    def get_cache_key(self, request, view):
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


class MagicLinkIPThrottle(SimpleRateThrottle):
    """
    Throttle magic link requests by client IP.
    """

    scope = "magic_link_ip"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return f"throttle:{self.scope}:{ident}"


class MagicLinkEmailThrottle(SimpleRateThrottle):
    """
    Throttle magic link requests by tenant and normalized email.
    """

    scope = "magic_link_email"

    def get_cache_key(self, request, view):
        email = (request.data.get("email") or "").strip().lower()

        website_id = getattr(
            getattr(request, "website", None),
            "pk",
            None,
        ) or getattr(
            getattr(getattr(request, "user", None), "website", None),
            "pk",
            None,
        ) or "global"

        if not email:
            ident = self.get_ident(request)
            return (
                f"throttle:{self.scope}:"
                f"website:{website_id}:ip:{ident}"
            )

        return (
            f"throttle:{self.scope}:"
            f"website:{website_id}:email:{email}"
        )
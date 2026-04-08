from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """
    Throttle login requests by authenticated user when available,
    otherwise by IP address.
    """

    scope = "login"

    def get_cache_key(self, request, view):
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
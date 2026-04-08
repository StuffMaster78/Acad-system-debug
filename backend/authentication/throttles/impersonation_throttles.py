from rest_framework.throttling import SimpleRateThrottle


class ImpersonationTokenCreateThrottle(SimpleRateThrottle):
    """
    Throttle impersonation token creation by staff user.
    """

    scope = "impersonation_token_create"

    def get_cache_key(self, request, view):
        website_id = getattr(
            getattr(request, "website", None),
            "pk",
            None,
        ) or "global"

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return (
                f"throttle:{self.scope}:"
                f"website:{website_id}:user:{user.pk}"
            )

        ident = self.get_ident(request)
        return (
            f"throttle:{self.scope}:"
            f"website:{website_id}:ip:{ident}"
        )


class ImpersonationStartThrottle(SimpleRateThrottle):
    """
    Throttle impersonation start attempts by staff user.
    """

    scope = "impersonation_start"

    def get_cache_key(self, request, view):
        website_id = getattr(
            getattr(request, "website", None),
            "pk",
            None,
        ) or "global"

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return (
                f"throttle:{self.scope}:"
                f"website:{website_id}:user:{user.pk}"
            )

        ident = self.get_ident(request)
        return (
            f"throttle:{self.scope}:"
            f"website:{website_id}:ip:{ident}"
        )
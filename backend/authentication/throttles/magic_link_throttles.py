from rest_framework.throttling import SimpleRateThrottle


class MagicLinkRequestThrottle(SimpleRateThrottle):
    """
    Throttle magic-link requests by email when present,
    otherwise by IP address.
    """

    scope = "magic_link_request"

    def get_cache_key(self, request, view):
        website_id = getattr(
            getattr(request, "website", None),
            "pk",
            None,
        ) or "global"

        email = (request.data.get("email") or "").strip().lower()
        if email:
            return (
                f"throttle:{self.scope}:"
                f"website:{website_id}:email:{email}"
            )

        ident = self.get_ident(request)
        return (
            f"throttle:{self.scope}:"
            f"website:{website_id}:ip:{ident}"
        )


class MagicLinkConfirmThrottle(SimpleRateThrottle):
    """
    Throttle magic-link confirmation attempts by IP.
    """

    scope = "magic_link_confirm"

    def get_cache_key(self, request, view):
        website_id = getattr(
            getattr(request, "website", None),
            "pk",
            None,
        ) or "global"

        ident = self.get_ident(request)
        return (
            f"throttle:{self.scope}:"
            f"website:{website_id}:ip:{ident}"
        )
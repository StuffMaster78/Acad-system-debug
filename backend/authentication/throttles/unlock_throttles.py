from rest_framework.throttling import SimpleRateThrottle


class AccountUnlockRequestThrottle(SimpleRateThrottle):
    """
    Throttle unlock-account requests by email when present,
    otherwise by IP address.
    """

    scope = "account_unlock_request"

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


class AccountUnlockConfirmThrottle(SimpleRateThrottle):
    """
    Throttle unlock confirmation attempts by IP.
    """

    scope = "account_unlock_confirm"

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
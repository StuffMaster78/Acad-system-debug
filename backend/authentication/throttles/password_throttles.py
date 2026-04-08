from rest_framework.throttling import SimpleRateThrottle


class PasswordResetRequestThrottle(SimpleRateThrottle):
    """
    Throttle password reset requests by normalized email when present,
    otherwise by IP address.
    """

    scope = "password_reset_request"

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
    
class PasswordResetConfirmThrottle(SimpleRateThrottle):
    """
    Throttle password reset confirmation attempts by IP.
    """

    scope = "password_reset_confirm"

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

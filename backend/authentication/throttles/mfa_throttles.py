from rest_framework.throttling import SimpleRateThrottle


class MFAChallengeThrottle(SimpleRateThrottle):
    """
    Throttle MFA challenge creation by authenticated user,
    otherwise by IP address.
    """

    scope = "mfa_challenge"

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


class MFAVerifyThrottle(SimpleRateThrottle):
    """
    Throttle MFA verification attempts by authenticated user,
    otherwise by IP address.
    """

    scope = "mfa_verify"

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


class BackupCodeGenerateThrottle(SimpleRateThrottle):
    """
    Throttle backup code regeneration by authenticated user.
    """

    scope = "backup_code_generate"

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

        return None
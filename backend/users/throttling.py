from rest_framework.throttling import SimpleRateThrottle


class LoginThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        if request.method == "POST":
            # Use IP address or email/username from POST data
            ident = request.data.get("email") or self.get_ident(request)
            return self.cache_format % {
                "scope": self.scope,
                "ident": ident
            }
        return None


class MagicLinkThrottle(SimpleRateThrottle):
    scope = "magic_link"

    def get_cache_key(self, request, view):
        if request.method == "POST":
            ident = request.data.get("email") or self.get_ident(request)
            return self.cache_format % {
                "scope": self.scope,
                "ident": ident
            }
        return None

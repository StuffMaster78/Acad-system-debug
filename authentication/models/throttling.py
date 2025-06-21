 
from rest_framework.throttling import SimpleRateThrottle

class LoginRateThrottle(SimpleRateThrottle):
    """Throttle for login requests."""
    scope = 'login'

    def get_cache_key(self, request, view):
        request.throttled_scope = self.scope  # add scope to request
        return self.get_ident(request)

class MagicLinkThrottle(SimpleRateThrottle):
    """Throttle for magic link requests."""
    scope = 'magic_link'

    def get_cache_key(self, request, view):
        request.throttled_scope = self.scope
        email = request.data.get('email')
        if email:
            return f'magic-link-{email}'
        return self.get_ident(request)
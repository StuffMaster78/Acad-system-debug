from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache

class LoginRateThrottle(SimpleRateThrottle):
    scope = 'login'

    def get_cache_key(self, request, view):
        request.throttled_scope = self.scope  # add scope to request
        return self.get_ident(request)
    
class LoginSustainedThrottle(SimpleRateThrottle):
    scope = "login_sustained"
    def get_cache_key(self, request, view):
        return self.get_ident(request)

class MagicLinkThrottle(SimpleRateThrottle):
    scope = 'magic_link'

    def get_cache_key(self, request, view):
        request.throttled_scope = self.scope
        email = request.data.get('email')
        if email:
            return f'magic-link-{email}'
        return self.get_ident(request)
    
    @staticmethod
    def clear_rate_limit(email):
        """
        Clear rate limit cache for a specific email.
        Useful for admin/testing purposes.
        """
        cache_key = f'throttle_magic-link-{email}'
        cache.delete(cache_key)
        return True


class PasswordResetRateThrottle(SimpleRateThrottle):
    scope = 'password_reset'

    def get_cache_key(self, request, view):
        return self.get_ident(request)  # uses IP address

class MFARateThrottle(SimpleRateThrottle):
    scope = 'mfa_challenge'

    def get_cache_key(self, request, view):
        return self.get_ident(request)
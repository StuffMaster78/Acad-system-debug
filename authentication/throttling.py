from rest_framework.throttling import SimpleRateThrottle

class LoginRateThrottle(SimpleRateThrottle):
    scope = 'login'

    def get_cache_key(self, request, view):
        request.throttled_scope = self.scope  # add scope to request
        return self.get_ident(request)

class MagicLinkThrottle(SimpleRateThrottle):
    scope = 'magic_link'

    def get_cache_key(self, request, view):
        request.throttled_scope = self.scope
        email = request.data.get('email')
        if email:
            return f'magic-link-{email}'
        return self.get_ident(request)


class PasswordResetRateThrottle(SimpleRateThrottle):
    scope = 'password_reset'

    def get_cache_key(self, request, view):
        return self.get_ident(request)  # uses IP address


class MagicLinkRateThrottle(SimpleRateThrottle):
    scope = 'magic_link'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class MFARateThrottle(SimpleRateThrottle):
    scope = 'mfa_challenge'

    def get_cache_key(self, request, view):
        return self.get_ident(request)
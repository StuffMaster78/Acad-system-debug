 
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

 


#  from rest_framework.throttling import SimpleRateThrottle

# class LoginRateThrottle(SimpleRateThrottle):
#     scope = 'login'

#     def get_cache_key(self, request, view):
#         # Using IP address for rate limiting
#         return request.META.get('REMOTE_ADDR')
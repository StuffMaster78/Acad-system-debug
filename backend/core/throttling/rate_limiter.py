"""
Comprehensive rate limiting throttling classes.
Provides different rate limiting strategies for different endpoint types.
"""

import logging
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from rest_framework.exceptions import Throttled
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from ipware import get_client_ip

logger = logging.getLogger(__name__)


class EndpointRateThrottle(UserRateThrottle):
    """
    Rate throttle based on endpoint path.
    Allows different limits for different endpoints.
    """
    scope = 'endpoint'
    
    def get_rate(self):
        """
        Get rate limit from endpoint configuration or default.
        """
        # This will be called with request in allow_request
        if hasattr(self, '_endpoint_rate'):
            return self._endpoint_rate
        return super().get_rate()
    
    def allow_request(self, request, view):
        """
        Check if request should be allowed based on endpoint-specific limits.
        """
        # Check endpoint-specific configuration
        endpoint_config = get_endpoint_rate_limit(request.path)
        if endpoint_config:
            # Temporarily set scope and rate for this request
            original_scope = self.scope
            self.scope = endpoint_config.get('scope', self.scope)
            if 'rate' in endpoint_config:
                self._endpoint_rate = endpoint_config['rate']
            
            try:
                allowed = super().allow_request(request, view)
                if not allowed:
                    # Log violation
                    wait_time = self.wait()
                    log_rate_limit_violation(request, self, self.scope, wait_time)
                return allowed
            finally:
                # Restore original scope
                self.scope = original_scope
                if hasattr(self, '_endpoint_rate'):
                    delattr(self, '_endpoint_rate')
        
        # Use default behavior
        return super().allow_request(request, view)
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on user and endpoint.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        # Get endpoint path
        endpoint = request.path
        # Normalize endpoint (remove trailing slashes, query params)
        endpoint = endpoint.rstrip('/').split('?')[0]
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': f"{ident}_{endpoint}"
        }


class IPRateThrottle(AnonRateThrottle):
    """
    Rate throttle based on IP address.
    Useful for anonymous users and preventing IP-based abuse.
    """
    scope = 'ip'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on IP address.
        """
        ip, _ = get_client_ip(request)
        if not ip:
            ip = 'unknown'
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ip
        }


class BurstRateThrottle(UserRateThrottle):
    """
    Short-term burst rate limiting.
    Prevents rapid-fire requests in a short time window.
    """
    scope = 'burst'
    
    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not allowed:
            wait_time = self.wait()
            log_rate_limit_violation(request, self, self.scope, wait_time)
        return allowed
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class SustainedRateThrottle(UserRateThrottle):
    """
    Long-term sustained rate limiting.
    Prevents excessive usage over longer periods.
    """
    scope = 'sustained'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class AdminRateThrottle(UserRateThrottle):
    """
    Higher rate limits for admin users.
    """
    scope = 'admin'
    
    def allow_request(self, request, view):
        """
        Only apply to admin users, otherwise allow.
        """
        if not request.user.is_authenticated:
            return True
        
        if request.user.role not in ['admin', 'superadmin']:
            return True
        
        return super().allow_request(request, view)
    
    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': request.user.pk
        }


class PublicEndpointThrottle(AnonRateThrottle):
    """
    Rate limiting for public endpoints (no auth required).
    Stricter limits to prevent abuse.
    """
    scope = 'public'
    
    def get_cache_key(self, request, view):
        ip, _ = get_client_ip(request)
        if not ip:
            ip = 'unknown'
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ip
        }


class WriteOperationThrottle(UserRateThrottle):
    """
    Rate limiting for write operations (POST, PUT, PATCH, DELETE).
    Stricter limits to prevent abuse and protect data integrity.
    """
    scope = 'write'
    
    def allow_request(self, request, view):
        """
        Only apply to write operations.
        """
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return True
        
        allowed = super().allow_request(request, view)
        if not allowed:
            wait_time = self.wait()
            log_rate_limit_violation(request, self, self.scope, wait_time)
        return allowed
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class ReadOperationThrottle(UserRateThrottle):
    """
    Rate limiting for read operations (GET, HEAD, OPTIONS).
    More lenient limits for read operations.
    """
    scope = 'read'
    
    def allow_request(self, request, view):
        """
        Only apply to read operations.
        """
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return super().allow_request(request, view)
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class CustomThrottled(Throttled):
    """
    Custom throttled exception with better error messages.
    """
    def __init__(self, wait=None, detail=None, scope=None):
        if detail is None:
            detail = self.default_detail
        
        if scope:
            detail = f"Rate limit exceeded for {scope}. {detail}"
        
        super().__init__(wait, detail)


class RateLimitMiddleware:
    """
    Middleware to add rate limit headers to responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add rate limit headers if available
        if hasattr(request, 'rate_limit_info'):
            info = request.rate_limit_info
            response['X-RateLimit-Limit'] = str(info.get('limit', ''))
            response['X-RateLimit-Remaining'] = str(info.get('remaining', ''))
            response['X-RateLimit-Reset'] = str(info.get('reset', ''))
        
        return response


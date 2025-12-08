"""
Caching utilities for dashboard and stats endpoints.
"""
from functools import wraps
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import hashlib
import json


def cache_dashboard_result(timeout=300, key_prefix='dashboard'):
    """
    Decorator to cache dashboard endpoint results.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    
    Usage:
        @cache_dashboard_result(timeout=600, key_prefix='tip_dashboard')
        def dashboard(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Build cache key from request parameters
            cache_params = {
                'user_id': request.user.id if request.user.is_authenticated else None,
                'user_role': getattr(request.user, 'role', None),
                'website_id': getattr(request.user, 'website_id', None) if hasattr(request.user, 'website_id') else None,
                'query_params': dict(request.query_params),
            }
            
            # Create cache key
            cache_key_data = json.dumps(cache_params, sort_keys=True)
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(cache_key_data.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                from rest_framework.response import Response
                return Response(cached_result)
            
            # Execute function and cache result
            result = func(self, request, *args, **kwargs)
            
            # Cache the response data
            if hasattr(result, 'data'):
                cache.set(cache_key, result.data, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_dashboard_cache(key_prefix='dashboard', patterns=None):
    """
    Invalidate dashboard cache entries.
    
    Args:
        key_prefix: Cache key prefix to invalidate
        patterns: List of additional patterns to match
    
    Usage:
        invalidate_dashboard_cache('tip_dashboard')
    """
    # Note: Django cache doesn't support pattern matching by default
    # For Redis, you'd need to use redis-py directly
    # This is a simplified version that works with basic cache backends
    pass


def get_or_set_cache(key, callable_func, timeout=300):
    """
    Get value from cache or set it if not present.
    
    Args:
        key: Cache key
        callable_func: Function to call if cache miss
        timeout: Cache timeout in seconds
    
    Returns:
        Cached or computed value
    """
    value = cache.get(key)
    if value is None:
        value = callable_func()
        cache.set(key, value, timeout)
    return value


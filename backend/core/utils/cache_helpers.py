"""
Caching utilities for optimizing database queries and API responses.
"""
from functools import wraps
from django.core.cache import cache
from django.utils.decorators import method_decorator
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def cache_result(timeout=300, key_prefix='cache', vary_on=None):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
        vary_on: List of function argument names to include in cache key
    
    Usage:
        @cache_result(timeout=600, key_prefix='dashboard', vary_on=['user_id', 'days'])
        def get_dashboard_stats(user_id, days=30):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            cache_params = {}
            
            # Include function name
            cache_params['func'] = func.__name__
            
            # Include vary_on arguments
            if vary_on:
                for arg_name in vary_on:
                    if arg_name in kwargs:
                        cache_params[arg_name] = kwargs[arg_name]
                    elif len(args) > 0 and hasattr(args[0], arg_name):
                        # For instance methods, get from self
                        cache_params[arg_name] = getattr(args[0], arg_name, None)
            
            # Include all kwargs if no vary_on specified
            if not vary_on:
                cache_params.update(kwargs)
            
            # Create cache key
            cache_key_data = json.dumps(cache_params, sort_keys=True, default=str)
            cache_key = f"{key_prefix}:{hashlib.md5(cache_key_data.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function
            logger.debug(f"Cache miss for {cache_key}, executing function")
            result = func(*args, **kwargs)
            
            # Cache the result
            try:
                cache.set(cache_key, result, timeout)
            except Exception as e:
                logger.warning(f"Failed to cache result for {cache_key}: {e}")
            
            return result
        return wrapper
    return decorator


def cache_view_result(timeout=300, key_prefix='view'):
    """
    Decorator to cache DRF viewset action results.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
    
    Usage:
        @action(detail=False, methods=['get'])
        @cache_view_result(timeout=600, key_prefix='dashboard')
        def dashboard(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Build cache key from request
            cache_params = {
                'user_id': request.user.id if request.user.is_authenticated else None,
                'user_role': getattr(request.user, 'role', None),
                'website_id': getattr(request.user, 'website_id', None) if hasattr(request.user, 'website_id') else None,
                'query_params': dict(request.query_params),
                'action': func.__name__,
            }
            
            # Create cache key
            cache_key_data = json.dumps(cache_params, sort_keys=True, default=str)
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(cache_key_data.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                from rest_framework.response import Response
                logger.debug(f"Cache hit for {cache_key}")
                return Response(cached_result)
            
            # Execute function
            logger.debug(f"Cache miss for {cache_key}, executing function")
            result = func(self, request, *args, **kwargs)
            
            # Cache the response data
            if hasattr(result, 'data'):
                try:
                    cache.set(cache_key, result.data, timeout)
                except Exception as e:
                    logger.warning(f"Failed to cache result for {cache_key}: {e}")
            
            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern.
    
    Note: This requires Redis with pattern matching support.
    For other cache backends, you may need to track keys manually.
    
    Args:
        pattern: Cache key pattern (e.g., 'dashboard:*')
    """
    try:
        # Try to use Redis pattern matching
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
            logger.info(f"Invalidated cache pattern: {pattern}")
        else:
            logger.warning(f"Cache backend does not support pattern deletion: {pattern}")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")


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
    if value is not None:
        return value
    
    value = callable_func()
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        logger.warning(f"Failed to cache value for {key}: {e}")
    
    return value


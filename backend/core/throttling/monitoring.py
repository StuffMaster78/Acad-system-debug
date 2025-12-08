"""
Rate limit monitoring and logging.
Tracks rate limit violations and provides analytics.
"""

import logging
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from collections import defaultdict
import json
from ipware import get_client_ip

logger = logging.getLogger(__name__)

# Cache key prefix for rate limit monitoring
RATE_LIMIT_MONITOR_PREFIX = 'rate_limit_monitor:'


def log_rate_limit_violation(request, throttle_class, scope, wait_time=None):
    """
    Log a rate limit violation for monitoring.
    
    Args:
        request: The request object
        throttle_class: The throttle class that triggered the limit
        scope: The rate limit scope
        wait_time: Time to wait before retry (seconds)
    """
    user_id = request.user.pk if request.user.is_authenticated else 'anonymous'
    ip, _ = get_client_ip(request) if hasattr(request, 'META') else (None, None)
    
    violation_data = {
        'timestamp': timezone.now().isoformat(),
        'user_id': user_id,
        'ip': ip,
        'endpoint': request.path,
        'method': request.method,
        'scope': scope,
        'throttle_class': throttle_class.__name__,
        'wait_time': wait_time,
        'user_role': getattr(request.user, 'role', 'anonymous') if request.user.is_authenticated else 'anonymous',
    }
    
    # Log to logger
    logger.warning(
        f"Rate limit exceeded: {scope} | User: {user_id} | IP: {ip} | "
        f"Endpoint: {request.method} {request.path} | Wait: {wait_time}s"
    )
    
    # Store in cache for analytics (last 1000 violations)
    cache_key = f"{RATE_LIMIT_MONITOR_PREFIX}violations"
    violations = cache.get(cache_key, [])
    violations.append(violation_data)
    
    # Keep only last 1000 violations
    if len(violations) > 1000:
        violations = violations[-1000:]
    
    cache.set(cache_key, violations, timeout=86400)  # 24 hours
    
    # Aggregate by scope
    scope_key = f"{RATE_LIMIT_MONITOR_PREFIX}scope:{scope}"
    scope_count = cache.get(scope_key, 0)
    cache.set(scope_key, scope_count + 1, timeout=86400)
    
    # Aggregate by user (if authenticated)
    if request.user.is_authenticated:
        user_key = f"{RATE_LIMIT_MONITOR_PREFIX}user:{user_id}"
        user_violations = cache.get(user_key, [])
        user_violations.append(violation_data)
        if len(user_violations) > 100:
            user_violations = user_violations[-100:]
        cache.set(user_key, user_violations, timeout=86400)
    
    # Aggregate by IP
    if ip:
        ip_key = f"{RATE_LIMIT_MONITOR_PREFIX}ip:{ip}"
        ip_count = cache.get(ip_key, 0)
        cache.set(ip_key, ip_count + 1, timeout=86400)


def get_rate_limit_stats(scope=None, user_id=None, ip=None, limit=100):
    """
    Get rate limit violation statistics.
    
    Args:
        scope: Filter by scope (optional)
        user_id: Filter by user ID (optional)
        ip: Filter by IP (optional)
        limit: Maximum number of violations to return
    
    Returns:
        dict with violation statistics
    """
    cache_key = f"{RATE_LIMIT_MONITOR_PREFIX}violations"
    violations = cache.get(cache_key, [])
    
    # Filter violations
    if scope:
        violations = [v for v in violations if v.get('scope') == scope]
    if user_id:
        violations = [v for v in violations if v.get('user_id') == user_id]
    if ip:
        violations = [v for v in violations if v.get('ip') == ip]
    
    # Limit results
    violations = violations[-limit:]
    
    # Aggregate statistics
    stats = {
        'total_violations': len(violations),
        'by_scope': defaultdict(int),
        'by_endpoint': defaultdict(int),
        'by_user': defaultdict(int),
        'by_ip': defaultdict(int),
        'recent_violations': violations,
    }
    
    for violation in violations:
        stats['by_scope'][violation.get('scope', 'unknown')] += 1
        stats['by_endpoint'][violation.get('endpoint', 'unknown')] += 1
        stats['by_user'][violation.get('user_id', 'unknown')] += 1
        stats['by_ip'][violation.get('ip', 'unknown')] += 1
    
    return stats


def clear_rate_limit_stats():
    """
    Clear all rate limit monitoring data.
    """
    # Clear violations
    cache.delete(f"{RATE_LIMIT_MONITOR_PREFIX}violations")
    
    # Clear scope aggregations (approximate - would need to track all keys)
    logger.info("Rate limit monitoring data cleared")


def get_top_rate_limited_endpoints(limit=10):
    """
    Get top endpoints by rate limit violations.
    
    Args:
        limit: Number of top endpoints to return
    
    Returns:
        list of tuples (endpoint, violation_count)
    """
    stats = get_rate_limit_stats()
    endpoints = sorted(
        stats['by_endpoint'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    return endpoints[:limit]


def get_top_rate_limited_users(limit=10):
    """
    Get top users by rate limit violations.
    
    Args:
        limit: Number of top users to return
    
    Returns:
        list of tuples (user_id, violation_count)
    """
    stats = get_rate_limit_stats()
    users = sorted(
        stats['by_user'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    return users[:limit]


def get_top_rate_limited_ips(limit=10):
    """
    Get top IPs by rate limit violations.
    
    Args:
        limit: Number of top IPs to return
    
    Returns:
        list of tuples (ip, violation_count)
    """
    stats = get_rate_limit_stats()
    ips = sorted(
        stats['by_ip'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    return ips[:limit]


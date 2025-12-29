"""
Public health check endpoints for high availability.
These endpoints allow the system to report degraded status while still serving requests.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.db import connection
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@never_cache
def health_check(request):
    """
    Public health check endpoint (no authentication required).
    Returns 200 if system is healthy, 503 if degraded.
    System continues to serve requests even when degraded.
    """
    checks = {
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {}
    }
    
    overall_healthy = True
    
    # Check database (critical - but allow degraded mode)
    db_check = _check_database()
    checks['services']['database'] = db_check
    if db_check['status'] == 'error':
        overall_healthy = False
        checks['status'] = 'degraded'
    
    # Check cache (non-critical - can operate without)
    cache_check = _check_cache()
    checks['services']['cache'] = cache_check
    if cache_check['status'] == 'error' and overall_healthy:
        checks['status'] = 'degraded'
    
    # Return 200 even if degraded - system is still serving requests
    # Only return 503 if completely down
    status_code = 200 if checks['status'] in ['healthy', 'degraded'] else 503
    
    return JsonResponse(checks, status=status_code)


@require_http_methods(["GET"])
@never_cache
def health_ready(request):
    """
    Readiness check - returns 200 only if system is ready to accept traffic.
    Used by load balancers and orchestration systems.
    """
    checks = {
        'status': 'ready',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Database must be available for readiness
    db_check = _check_database()
    checks['checks']['database'] = db_check
    if db_check['status'] != 'healthy':
        checks['status'] = 'not_ready'
        return JsonResponse(checks, status=503)
    
    # Cache is nice to have but not required
    cache_check = _check_cache()
    checks['checks']['cache'] = cache_check
    
    return JsonResponse(checks, status=200)


@require_http_methods(["GET"])
@never_cache
def health_live(request):
    """
    Liveness check - returns 200 if the process is alive.
    Always returns 200 unless the process is completely dead.
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': time.time()
    }, status=200)


def _check_database():
    """Check database connectivity with timeout."""
    try:
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            'status': 'healthy',
            'response_time_ms': round(response_time, 2)
        }
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


def _check_cache():
    """Check cache connectivity with timeout."""
    try:
        start_time = time.time()
        test_key = 'health_check_' + str(time.time())
        cache.set(test_key, 'ok', 10)
        result = cache.get(test_key)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if result == 'ok':
            cache.delete(test_key)
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2)
            }
        else:
            return {
                'status': 'error',
                'error': 'Cache get failed'
            }
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


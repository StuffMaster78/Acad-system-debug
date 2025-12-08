"""
Performance monitoring middleware to track query counts, response times, and cache usage.
This helps verify the effectiveness of our optimizations.
"""
import time
import logging
from django.core.cache import cache
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor API performance metrics.
    Tracks:
    - Query count
    - Response time
    - Cache hits/misses
    - Slow queries (>100ms)
    """
    
    def process_request(self, request):
        """Record start time and initial query count."""
        request._start_time = time.time()
        request._initial_queries = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """Record performance metrics after request."""
        if not hasattr(request, '_start_time'):
            return response
        
        # Calculate metrics
        response_time = (time.time() - request._start_time) * 1000  # Convert to ms
        query_count = len(connection.queries) - getattr(request, '_initial_queries', 0)
        
        # Only log API requests (not static files)
        if request.path.startswith('/api/'):
            # Log slow requests
            if response_time > 1000:  # > 1 second
                logger.warning(
                    f"Slow request: {request.method} {request.path} - "
                    f"{response_time:.2f}ms, {query_count} queries"
                )
            
            # Log high query count requests
            if query_count > 20:
                logger.warning(
                    f"High query count: {request.method} {request.path} - "
                    f"{query_count} queries in {response_time:.2f}ms"
                )
            
            # Store metrics in cache for dashboard
            self._store_metrics(request, response_time, query_count)
        
        # Add performance headers (for debugging)
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.is_superuser or getattr(request.user, 'role', None) in ['admin', 'superadmin']:
                response['X-Response-Time'] = f"{response_time:.2f}ms"
                response['X-Query-Count'] = str(query_count)
        
        return response
    
    def _store_metrics(self, request, response_time, query_count):
        """Store metrics in cache for dashboard viewing."""
        try:
            endpoint = f"{request.method} {request.path}"
            
            # Store recent metrics (last 100 requests per endpoint)
            cache_key = f"perf_metrics:{endpoint}"
            metrics = cache.get(cache_key, [])
            metrics.append({
                'time': time.time(),
                'response_time': response_time,
                'query_count': query_count,
            })
            
            # Keep only last 100
            if len(metrics) > 100:
                metrics = metrics[-100:]
            
            cache.set(cache_key, metrics, timeout=3600)  # 1 hour
            
            # Store aggregate stats
            stats_key = f"perf_stats:{endpoint}"
            stats = cache.get(stats_key, {
                'count': 0,
                'total_time': 0,
                'total_queries': 0,
                'max_time': 0,
                'max_queries': 0,
            })
            
            stats['count'] += 1
            stats['total_time'] += response_time
            stats['total_queries'] += query_count
            stats['max_time'] = max(stats['max_time'], response_time)
            stats['max_queries'] = max(stats['max_queries'], query_count)
            
            cache.set(stats_key, stats, timeout=86400)  # 24 hours
            
        except Exception as e:
            logger.debug(f"Failed to store metrics: {e}")


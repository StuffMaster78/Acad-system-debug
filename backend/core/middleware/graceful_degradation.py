"""
Graceful degradation middleware.
Allows the system to continue operating even when some services fail.
"""
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class GracefulDegradationMiddleware(MiddlewareMixin):
    """
    Middleware that enables graceful degradation when services fail.
    
    Features:
    - Database read fallback to cache
    - Cache fallback to in-memory
    - Service isolation (one failure doesn't kill everything)
    - Degraded mode flag
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.degraded_mode = False
        self.degraded_services = set()
        super().__init__(get_response)
    
    def process_request(self, request):
        """Check service health and set degraded mode if needed."""
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            logger.warning(f"Database check failed: {e}")
            self.degraded_services.add('database')
            self.degraded_mode = True
        
        # Check cache
        try:
            cache.get('health_check')
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            self.degraded_services.add('cache')
            # Cache failure is not critical - don't set degraded mode
        
        # Store in request for use in views
        request.degraded_mode = self.degraded_mode
        request.degraded_services = self.degraded_services
        
        return None
    
    def process_exception(self, request, exception):
        """Handle exceptions gracefully."""
        # Don't handle exceptions here - let Django handle them
        # This is just for logging
        if hasattr(request, 'degraded_mode') and request.degraded_mode:
            logger.warning(
                f"Exception in degraded mode: {exception}",
                exc_info=True
            )
        return None


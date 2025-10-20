"""
Real-time performance dashboard views.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
from notifications_system.monitoring.performance import get_performance_monitor
from notifications_system.analytics.template_analytics import get_template_analytics
from notifications_system.caching.template_cache import get_cache_manager
from notifications_system.delivery.sse import get_connection_manager

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PerformanceDashboardView(View):
    """Real-time performance dashboard."""
    
    def get(self, request):
        """Get dashboard data."""
        try:
            # Get performance metrics
            monitor = get_performance_monitor()
            performance_stats = monitor.get_notification_stats()
            
            # Get template analytics
            analytics = get_template_analytics()
            template_stats = analytics.get_template_stats(
                request.GET.get('event_key', ''),
                days=int(request.GET.get('days', 30)),
                website_id=request.GET.get('website_id')
            )
            
            # Get cache stats
            cache_manager = get_cache_manager()
            cache_stats = cache_manager.cache.get_cache_stats()
            
            # Get SSE connection stats
            connection_manager = get_connection_manager()
            sse_stats = {
                'active_connections': len(connection_manager.get_all_connections()),
                'total_connections': sum(
                    len(connections) for connections in connection_manager.get_all_connections().values()
                )
            }
            
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'performance': performance_stats,
                'templates': template_stats,
                'cache': cache_stats,
                'sse': sse_stats,
                'system_health': self._get_system_health()
            }
            
            return JsonResponse(dashboard_data)
            
        except Exception as e:
            logger.exception(f"Dashboard error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        try:
            # Check database connection
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_healthy = True
        except Exception:
            db_healthy = False
        
        # Check Redis connection
        try:
            cache.set('health_check', 'ok', 10)
            redis_healthy = cache.get('health_check') == 'ok'
        except Exception:
            redis_healthy = False
        
        return {
            'database': db_healthy,
            'redis': redis_healthy,
            'overall': db_healthy and redis_healthy
        }


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class RealTimeMetricsView(View):
    """Real-time metrics stream."""
    
    def get(self, request):
        """Stream real-time metrics."""
        def metrics_generator():
            """Generate real-time metrics."""
            try:
                while True:
                    # Get current metrics
                    monitor = get_performance_monitor()
                    performance_stats = monitor.get_notification_stats()
                    
                    # Get cache stats
                    cache_manager = get_cache_manager()
                    cache_stats = cache_manager.cache.get_cache_stats()
                    
                    # Get SSE stats
                    connection_manager = get_connection_manager()
                    sse_stats = {
                        'active_connections': len(connection_manager.get_all_connections()),
                        'total_connections': sum(
                            len(connections) for connections in connection_manager.get_all_connections().values()
                        )
                    }
                    
                    metrics = {
                        'timestamp': datetime.now().isoformat(),
                        'performance': performance_stats,
                        'cache': cache_stats,
                        'sse': sse_stats
                    }
                    
                    yield f"data: {json.dumps(metrics)}\n\n"
                    
                    # Wait 5 seconds before next update
                    import time
                    time.sleep(5)
                    
            except GeneratorExit:
                logger.debug("Real-time metrics stream closed")
            except Exception as e:
                logger.exception(f"Real-time metrics error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        response = StreamingHttpResponse(
            metrics_generator(),
            content_type='text/event-stream'
        )
        
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        response['Access-Control-Allow-Origin'] = '*'
        
        return response


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class TemplateAnalyticsView(View):
    """Template analytics dashboard."""
    
    def get(self, request):
        """Get template analytics data."""
        try:
            analytics = get_template_analytics()
            
            # Get parameters
            event_key = request.GET.get('event_key', '')
            days = int(request.GET.get('days', 30))
            website_id = request.GET.get('website_id')
            limit = int(request.GET.get('limit', 10))
            metric = request.GET.get('metric', 'render_count')
            
            # Get analytics data
            if event_key:
                stats = analytics.get_template_stats(event_key, days, website_id)
                trends = analytics.get_template_trends(event_key, days, website_id)
                
                data = {
                    'stats': stats,
                    'trends': trends,
                    'type': 'single_event'
                }
            else:
                top_templates = analytics.get_top_templates(limit, days, website_id, metric)
                
                data = {
                    'top_templates': top_templates,
                    'type': 'overview'
                }
            
            return JsonResponse(data)
            
        except Exception as e:
            logger.exception(f"Template analytics error: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CacheManagementView(View):
    """Cache management interface."""
    
    def get(self, request):
        """Get cache statistics and status."""
        try:
            cache_manager = get_cache_manager()
            cache_stats = cache_manager.cache.get_cache_stats()
            
            # Get cache keys (this would need proper implementation)
            cache_keys = self._get_cache_keys()
            
            data = {
                'stats': cache_stats,
                'keys': cache_keys,
                'timestamp': datetime.now().isoformat()
            }
            
            return JsonResponse(data)
            
        except Exception as e:
            logger.exception(f"Cache management error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Clear cache or perform cache operations."""
        try:
            action = request.POST.get('action')
            
            if action == 'clear_all':
                cache_manager = get_cache_manager()
                cache_manager.cache.clear_cache()
                return JsonResponse({'status': 'success', 'message': 'Cache cleared'})
            
            elif action == 'clear_pattern':
                pattern = request.POST.get('pattern')
                if pattern:
                    cache_manager = get_cache_manager()
                    cache_manager.cache.invalidate_pattern(pattern)
                    return JsonResponse({'status': 'success', 'message': f'Pattern {pattern} cleared'})
            
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
        except Exception as e:
            logger.exception(f"Cache operation error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def _get_cache_keys(self) -> List[str]:
        """Get list of cache keys (simplified implementation)."""
        # This would need proper Redis SCAN implementation
        return ['template:order.assigned:email', 'template:user.welcome:email']


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SystemHealthView(View):
    """System health monitoring."""
    
    def get(self, request):
        """Get system health status."""
        try:
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'services': self._check_services(),
                'performance': self._check_performance(),
                'alerts': self._get_alerts()
            }
            
            return JsonResponse(health_data)
            
        except Exception as e:
            logger.exception(f"System health error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def _check_services(self) -> Dict[str, Any]:
        """Check service health."""
        services = {}
        
        # Database
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            services['database'] = {'status': 'healthy', 'response_time': 0}
        except Exception as e:
            services['database'] = {'status': 'unhealthy', 'error': str(e)}
        
        # Redis
        try:
            import time
            start = time.time()
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            response_time = time.time() - start
            services['redis'] = {
                'status': 'healthy' if result == 'ok' else 'unhealthy',
                'response_time': response_time
            }
        except Exception as e:
            services['redis'] = {'status': 'unhealthy', 'error': str(e)}
        
        return services
    
    def _check_performance(self) -> Dict[str, Any]:
        """Check performance metrics."""
        monitor = get_performance_monitor()
        stats = monitor.get_notification_stats()
        
        # Check if metrics are within acceptable ranges
        performance_issues = []
        
        for metric_name, metric_stats in stats.items():
            if metric_stats.get('avg', 0) > 1000:  # > 1 second
                performance_issues.append(f"{metric_name} average time too high")
        
        return {
            'status': 'healthy' if not performance_issues else 'degraded',
            'issues': performance_issues,
            'metrics': stats
        }
    
    def _get_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts."""
        alerts = []
        
        # Check for high error rates
        try:
            analytics = get_template_analytics()
            # This would check for high error rates across templates
            # For now, return empty list
            pass
        except Exception as e:
            alerts.append({
                'level': 'error',
                'message': f'Analytics service error: {e}',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts


# URL patterns for dashboard
dashboard_urlpatterns = [
    path('dashboard/', PerformanceDashboardView.as_view(), name='performance_dashboard'),
    path('dashboard/metrics/', RealTimeMetricsView.as_view(), name='realtime_metrics'),
    path('dashboard/templates/', TemplateAnalyticsView.as_view(), name='template_analytics'),
    path('dashboard/cache/', CacheManagementView.as_view(), name='cache_management'),
    path('dashboard/health/', SystemHealthView.as_view(), name='system_health'),
]

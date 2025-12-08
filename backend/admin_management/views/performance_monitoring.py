"""
Performance monitoring dashboard views.
Shows query counts, response times, cache statistics, and optimization effectiveness.
"""
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache
from django.db import connection
from django.conf import settings
import json
import time

from rest_framework import viewsets


class PerformanceMonitoringViewSet(viewsets.ViewSet):
    """
    ViewSet for viewing performance metrics and optimization effectiveness.
    """
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['get'], url_path='metrics')
    def get_metrics(self, request):
        """
        Get performance metrics for all endpoints.
        Shows response times, query counts, and cache statistics.
        """
        try:
            # Get all cached metrics
            cache_keys = []
            for key in cache.keys('perf_metrics:*'):
                cache_keys.append(key)
            
            endpoint_metrics = {}
            for key in cache_keys:
                endpoint = key.replace('perf_metrics:', '')
                metrics = cache.get(key, [])
                
                if metrics:
                    response_times = [m['response_time'] for m in metrics]
                    query_counts = [m['query_count'] for m in metrics]
                    
                    endpoint_metrics[endpoint] = {
                        'recent_requests': len(metrics),
                        'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
                        'min_response_time': min(response_times) if response_times else 0,
                        'max_response_time': max(response_times) if response_times else 0,
                        'avg_query_count': sum(query_counts) / len(query_counts) if query_counts else 0,
                        'min_query_count': min(query_counts) if query_counts else 0,
                        'max_query_count': max(query_counts) if query_counts else 0,
                    }
            
            return Response({
                'endpoints': endpoint_metrics,
                'timestamp': time.time(),
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='stats')
    def get_stats(self, request):
        """
        Get aggregate performance statistics.
        """
        try:
            # Get all cached stats
            cache_keys = []
            for key in cache.keys('perf_stats:*'):
                cache_keys.append(key)
            
            endpoint_stats = {}
            for key in cache_keys:
                endpoint = key.replace('perf_stats:', '')
                stats = cache.get(key, {})
                
                if stats and stats.get('count', 0) > 0:
                    endpoint_stats[endpoint] = {
                        'total_requests': stats.get('count', 0),
                        'avg_response_time': stats.get('total_time', 0) / stats.get('count', 1),
                        'avg_query_count': stats.get('total_queries', 0) / stats.get('count', 1),
                        'max_response_time': stats.get('max_time', 0),
                        'max_query_count': stats.get('max_queries', 0),
                    }
            
            # Get cache statistics
            cache_info = self._get_cache_info()
            
            # Get database connection info
            db_info = {
                'queries_in_session': len(connection.queries),
                'time_queries': sum(float(q.get('time', 0)) for q in connection.queries),
            }
            
            return Response({
                'endpoints': endpoint_stats,
                'cache': cache_info,
                'database': db_info,
                'timestamp': time.time(),
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='slow-endpoints')
    def get_slow_endpoints(self, request):
        """
        Get endpoints with slow response times (>500ms).
        """
        try:
            threshold = float(request.query_params.get('threshold', 500))  # ms
            
            cache_keys = []
            for key in cache.keys('perf_stats:*'):
                cache_keys.append(key)
            
            slow_endpoints = []
            for key in cache_keys:
                endpoint = key.replace('perf_stats:', '')
                stats = cache.get(key, {})
                
                if stats and stats.get('count', 0) > 0:
                    avg_time = stats.get('total_time', 0) / stats.get('count', 1)
                    if avg_time > threshold:
                        slow_endpoints.append({
                            'endpoint': endpoint,
                            'avg_response_time': avg_time,
                            'max_response_time': stats.get('max_time', 0),
                            'request_count': stats.get('count', 0),
                            'avg_query_count': stats.get('total_queries', 0) / stats.get('count', 1),
                        })
            
            # Sort by average response time (slowest first)
            slow_endpoints.sort(key=lambda x: x['avg_response_time'], reverse=True)
            
            return Response({
                'slow_endpoints': slow_endpoints,
                'threshold_ms': threshold,
                'timestamp': time.time(),
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='high-query-endpoints')
    def get_high_query_endpoints(self, request):
        """
        Get endpoints with high query counts (>10 queries).
        """
        try:
            threshold = int(request.query_params.get('threshold', 10))
            
            cache_keys = []
            for key in cache.keys('perf_stats:*'):
                cache_keys.append(key)
            
            high_query_endpoints = []
            for key in cache_keys:
                endpoint = key.replace('perf_stats:', '')
                stats = cache.get(key, {})
                
                if stats and stats.get('count', 0) > 0:
                    avg_queries = stats.get('total_queries', 0) / stats.get('count', 1)
                    if avg_queries > threshold:
                        high_query_endpoints.append({
                            'endpoint': endpoint,
                            'avg_query_count': avg_queries,
                            'max_query_count': stats.get('max_queries', 0),
                            'request_count': stats.get('count', 0),
                            'avg_response_time': stats.get('total_time', 0) / stats.get('count', 1),
                        })
            
            # Sort by average query count (highest first)
            high_query_endpoints.sort(key=lambda x: x['avg_query_count'], reverse=True)
            
            return Response({
                'high_query_endpoints': high_query_endpoints,
                'threshold': threshold,
                'timestamp': time.time(),
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='clear-metrics')
    def clear_metrics(self, request):
        """
        Clear all performance metrics (admin only).
        """
        try:
            # Clear all performance cache keys
            cache_keys = []
            for key in cache.keys('perf_metrics:*'):
                cache_keys.append(key)
            for key in cache.keys('perf_stats:*'):
                cache_keys.append(key)
            
            for key in cache_keys:
                cache.delete(key)
            
            return Response({
                'message': f'Cleared {len(cache_keys)} metric cache keys',
                'timestamp': time.time(),
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_cache_info(self):
        """Get cache statistics."""
        try:
            # Try to get Redis info if using Redis
            if hasattr(cache, 'get_client'):
                client = cache.get_client()
                if hasattr(client, 'info'):
                    info = client.info()
                    return {
                        'type': 'redis',
                        'connected_clients': info.get('connected_clients', 0),
                        'used_memory': info.get('used_memory_human', 'N/A'),
                        'keyspace_hits': info.get('keyspace_hits', 0),
                        'keyspace_misses': info.get('keyspace_misses', 0),
                    }
        except Exception:
            pass
        
        return {
            'type': 'default',
            'backend': str(type(cache).__name__),
        }


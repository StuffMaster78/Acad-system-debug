"""
API endpoints for compression monitoring and statistics.
Admin-only access to view compression metrics.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache
from django.conf import settings
import json

# Cache key prefix for compression monitoring
COMPRESSION_MONITOR_PREFIX = 'compression_monitor:'


class CompressionMonitoringViewSet(viewsets.ViewSet):
    """
    API endpoints for compression monitoring and statistics.
    Accessible only by admin users.
    """
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get compression statistics.
        
        Query parameters:
        - limit (int): Number of recent compressions to analyze (default: 1000)
        """
        limit = int(request.query_params.get('limit', 1000))
        
        # Get compression data from cache
        cache_key = f"{COMPRESSION_MONITOR_PREFIX}recent"
        compression_data = cache.get(cache_key, [])
        
        if not compression_data:
            return Response({
                'total_compressions': 0,
                'avg_compression_ratio': 0,
                'total_bytes_saved': 0,
                'total_original_size': 0,
                'total_compressed_size': 0,
                'settings': {
                    'compress_min_length': getattr(settings, 'COMPRESS_MIN_LENGTH', 200),
                    'compress_level': getattr(settings, 'COMPRESS_LEVEL', 6),
                }
            }, status=status.HTTP_200_OK)
        
        # Analyze recent compressions
        recent_data = compression_data[-limit:]
        
        total_compressions = len(recent_data)
        total_original = sum(d.get('original_size', 0) for d in recent_data)
        total_compressed = sum(d.get('compressed_size', 0) for d in recent_data)
        total_saved = total_original - total_compressed
        
        avg_ratio = (total_saved / total_original * 100) if total_original > 0 else 0
        
        # Group by endpoint
        endpoint_stats = {}
        for data in recent_data:
            endpoint = data.get('endpoint', 'unknown')
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'count': 0,
                    'total_original': 0,
                    'total_compressed': 0,
                    'total_saved': 0,
                }
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_original'] += data.get('original_size', 0)
            endpoint_stats[endpoint]['total_compressed'] += data.get('compressed_size', 0)
            endpoint_stats[endpoint]['total_saved'] += (
                data.get('original_size', 0) - data.get('compressed_size', 0)
            )
        
        # Calculate ratios for each endpoint
        for endpoint, stats in endpoint_stats.items():
            if stats['total_original'] > 0:
                stats['compression_ratio'] = (stats['total_saved'] / stats['total_original']) * 100
            else:
                stats['compression_ratio'] = 0
        
        return Response({
            'total_compressions': total_compressions,
            'avg_compression_ratio': round(avg_ratio, 2),
            'total_bytes_saved': total_saved,
            'total_original_size': total_original,
            'total_compressed_size': total_compressed,
            'total_saved_mb': round(total_saved / (1024 * 1024), 2),
            'endpoint_stats': endpoint_stats,
            'settings': {
                'compress_min_length': getattr(settings, 'COMPRESS_MIN_LENGTH', 200),
                'compress_level': getattr(settings, 'COMPRESS_LEVEL', 6),
                'compress_mimetypes': getattr(settings, 'COMPRESS_MIMETYPES', []),
            }
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='clear-stats')
    def clear_stats(self, request):
        """
        Clear compression monitoring data.
        """
        cache_key = f"{COMPRESSION_MONITOR_PREFIX}recent"
        cache.delete(cache_key)
        return Response(
            {"message": "Compression statistics cleared successfully."},
            status=status.HTTP_200_OK
        )


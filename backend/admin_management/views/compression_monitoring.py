from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache
from django.conf import settings

COMPRESSION_MONITOR_PREFIX = 'compression_monitor:'
DEFAULT_LIMIT = 1000


class CompressionMonitoringViewSet(viewsets.ViewSet):
    """Admin-only endpoints for compression monitoring and statistics."""

    permission_classes = [IsAdminUser]

    def _get_compression_settings(self):
        return {
            'compress_min_length': getattr(settings, 'COMPRESS_MIN_LENGTH', 200),
            'compress_level': getattr(settings, 'COMPRESS_LEVEL', 6),
            'compress_mimetypes': getattr(settings, 'COMPRESS_MIMETYPES', []),
        }

    def _compute_ratio(self, original, saved):
        return round((saved / original * 100), 2) if original > 0 else 0

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get compression statistics.
        Query param: limit (int) — number of recent compressions to analyze.
        """
        try:
            limit = int(request.query_params.get('limit', DEFAULT_LIMIT))
            if limit <= 0:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "limit must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f"{COMPRESSION_MONITOR_PREFIX}recent"
        compression_data = cache.get(cache_key, [])

        if not compression_data:
            return Response({
                'total_compressions': 0,
                'avg_compression_ratio': 0,
                'total_bytes_saved': 0,
                'total_original_size': 0,
                'total_compressed_size': 0,
                'settings': self._get_compression_settings(),
            }, status=status.HTTP_200_OK)

        recent_data = compression_data[-limit:]
        total_original = sum(d.get('original_size', 0) for d in recent_data)
        total_compressed = sum(d.get('compressed_size', 0) for d in recent_data)
        total_saved = total_original - total_compressed

        endpoint_stats = {}
        for entry in recent_data:
            endpoint = entry.get('endpoint', 'unknown')
            ep = endpoint_stats.setdefault(endpoint, {
                'count': 0,
                'total_original': 0,
                'total_compressed': 0,
                'total_saved': 0,
                'compression_ratio': 0,
            })
            ep['count'] += 1
            original = entry.get('original_size', 0)
            compressed = entry.get('compressed_size', 0)
            ep['total_original'] += original
            ep['total_compressed'] += compressed
            ep['total_saved'] += original - compressed
            ep['compression_ratio'] = self._compute_ratio(
                ep['total_original'], ep['total_saved']
            )

        return Response({
            'total_compressions': len(recent_data),
            'avg_compression_ratio': self._compute_ratio(total_original, total_saved),
            'total_bytes_saved': total_saved,
            'total_original_size': total_original,
            'total_compressed_size': total_compressed,
            'total_saved_mb': round(total_saved / (1024 * 1024), 2),
            'endpoint_stats': endpoint_stats,
            'settings': self._get_compression_settings(),
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='clear-stats')
    def clear_stats(self, request):
        """Clear all compression monitoring data."""
        cache.delete(f"{COMPRESSION_MONITOR_PREFIX}recent")
        return Response(
            {"message": "Compression statistics cleared successfully."},
            status=status.HTTP_200_OK
        )
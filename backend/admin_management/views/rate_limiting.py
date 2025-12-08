"""
API endpoints for rate limiting monitoring and management.
Admin-only access to view rate limit statistics and violations.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from core.throttling.monitoring import (
    get_rate_limit_stats,
    clear_rate_limit_stats,
    get_top_rate_limited_endpoints,
    get_top_rate_limited_users,
    get_top_rate_limited_ips,
)


class RateLimitingViewSet(viewsets.ViewSet):
    """
    API endpoints for rate limiting monitoring and management.
    Accessible only by admin users.
    """
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get overall rate limit violation statistics.
        
        Query parameters:
        - scope (str): Filter by scope
        - user_id (int): Filter by user ID
        - ip (str): Filter by IP address
        - limit (int): Maximum number of violations to return (default: 100)
        """
        scope = request.query_params.get('scope')
        user_id = request.query_params.get('user_id')
        ip = request.query_params.get('ip')
        limit = int(request.query_params.get('limit', 100))
        
        stats = get_rate_limit_stats(
            scope=scope,
            user_id=int(user_id) if user_id else None,
            ip=ip,
            limit=limit
        )
        
        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='top-endpoints')
    def top_endpoints(self, request):
        """
        Get top endpoints by rate limit violations.
        
        Query parameters:
        - limit (int): Number of top endpoints to return (default: 10)
        """
        limit = int(request.query_params.get('limit', 10))
        endpoints = get_top_rate_limited_endpoints(limit=limit)
        
        return Response({
            'endpoints': [
                {'endpoint': endpoint, 'violations': count}
                for endpoint, count in endpoints
            ]
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='top-users')
    def top_users(self, request):
        """
        Get top users by rate limit violations.
        
        Query parameters:
        - limit (int): Number of top users to return (default: 10)
        """
        limit = int(request.query_params.get('limit', 10))
        users = get_top_rate_limited_users(limit=limit)
        
        return Response({
            'users': [
                {'user_id': user_id, 'violations': count}
                for user_id, count in users
            ]
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='top-ips')
    def top_ips(self, request):
        """
        Get top IPs by rate limit violations.
        
        Query parameters:
        - limit (int): Number of top IPs to return (default: 10)
        """
        limit = int(request.query_params.get('limit', 10))
        ips = get_top_rate_limited_ips(limit=limit)
        
        return Response({
            'ips': [
                {'ip': ip, 'violations': count}
                for ip, count in ips
            ]
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='clear-stats')
    def clear_stats(self, request):
        """
        Clear all rate limit monitoring data.
        """
        clear_rate_limit_stats()
        return Response(
            {"message": "Rate limit statistics cleared successfully."},
            status=status.HTTP_200_OK
        )


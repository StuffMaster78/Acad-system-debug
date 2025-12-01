"""
System health monitoring views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from authentication.permissions import IsAdmin, IsSuperadminOrAdmin
from admin_management.services.system_health_service import SystemHealthService


class SystemHealthViewSet(viewsets.ViewSet):
    """
    ViewSet for system health monitoring.
    Admin and superadmin only.
    """
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """Get comprehensive system health metrics."""
        try:
            health_data = SystemHealthService.get_system_health()
            return Response(health_data)
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='alerts')
    def alerts(self, request):
        """Get system alerts only."""
        try:
            health_data = SystemHealthService.get_system_health()
            return Response({
                'alerts': health_data.get('alerts', []),
                'recommendations': health_data.get('recommendations', [])
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


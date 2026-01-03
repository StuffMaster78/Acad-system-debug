"""
Views for client badge management and analytics.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from client_management.models import ClientProfile
from client_management.services.client_badge_service import ClientBadgeService
from loyalty_management.models import ClientBadge
try:
    from loyalty_management.serializers import ClientBadgeSerializer
except ImportError:
    # Fallback if serializer doesn't exist
    from rest_framework import serializers
    from loyalty_management.models import ClientBadge
    
    class ClientBadgeSerializer(serializers.ModelSerializer):
        client_username = serializers.CharField(source='client.user.username', read_only=True)
        
        class Meta:
            model = ClientBadge
            fields = ['id', 'client', 'client_username', 'badge_name', 'description', 'awarded_at']
            read_only_fields = ['id', 'awarded_at']
from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)


class ClientBadgeViewSet(viewsets.ViewSet):
    """ViewSet for client badge management."""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get badges for the current client."""
        try:
            try:
                client = ClientProfile.objects.get(user=request.user)
            except ClientProfile.DoesNotExist:
                return Response(
                    {"error": "Client profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            badges = ClientBadgeService.get_client_badges(client)
            serializer = ClientBadgeSerializer(badges, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting client badges: {e}")
            return Response(
                {"error": "Failed to get client badges"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get badge statistics for the current client."""
        try:
            try:
                client = ClientProfile.objects.get(user=request.user)
            except ClientProfile.DoesNotExist:
                return Response(
                    {"error": "Client profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            stats = ClientBadgeService.get_badge_statistics(client)
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting client badge statistics: {e}")
            return Response(
                {"error": "Failed to get badge statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def evaluate(self, request):
        """Manually trigger badge evaluation for the current client."""
        try:
            try:
                client = ClientProfile.objects.get(user=request.user)
            except ClientProfile.DoesNotExist:
                return Response(
                    {"error": "Client profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            awarded = ClientBadgeService.evaluate_and_award_badges(client)
            return Response(
                {
                    "message": f"Evaluated badges. {len(awarded)} new badges awarded.",
                    "awarded": awarded
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error evaluating client badges: {e}")
            return Response(
                {"error": "Failed to evaluate badges"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClientBadgeAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for client badge analytics (admin only)."""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get badge distribution analytics."""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get badge distribution
            badge_distribution = ClientBadge.objects.values('badge_name').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Get total clients with badges
            total_clients_with_badges = ClientBadge.objects.values('client').distinct().count()
            
            # Get most common badges
            most_common = list(badge_distribution[:10])
            
            return Response({
                'total_badges_awarded': ClientBadge.objects.count(),
                'total_clients_with_badges': total_clients_with_badges,
                'badge_distribution': most_common
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting badge analytics: {e}")
            return Response(
                {"error": "Failed to get badge analytics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


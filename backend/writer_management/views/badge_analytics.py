# writer_management/views/badge_analytics.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from writer_management.analytics.badge_analytics import BadgeAnalyticsService
from writer_management.analytics.badge_achievements import BadgeAchievementService
from writer_management.models.profile import WriterProfile
from writer_management.models.badges import WriterBadge
from django.db.models import Count
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BadgeAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for badge analytics and insights."""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get comprehensive badge analytics."""
        try:
            analytics = BadgeAnalyticsService.get_badge_insights()
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting badge analytics: {e}")
            return Response(
                {"error": "Failed to get badge analytics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def distribution(self, request):
        """Get badge distribution analytics."""
        try:
            distribution = BadgeAnalyticsService.get_badge_distribution()
            return Response(distribution, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting badge distribution: {e}")
            return Response(
                {"error": "Failed to get badge distribution"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get badge trends over time."""
        try:
            days = int(request.query_params.get('days', 30))
            trends = BadgeAnalyticsService.get_badge_trends(days)
            return Response(trends, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting badge trends: {e}")
            return Response(
                {"error": "Failed to get badge trends"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get badge leaderboard."""
        try:
            badge_type = request.query_params.get('type', None)
            limit = int(request.query_params.get('limit', 10))
            leaderboard = BadgeAnalyticsService.get_badge_leaderboard(badge_type, limit)
            return Response(leaderboard, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting badge leaderboard: {e}")
            return Response(
                {"error": "Failed to get badge leaderboard"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def achievements(self, request):
        """Get badge achievement statistics."""
        try:
            achievements = BadgeAnalyticsService.get_badge_achievements()
            return Response(achievements, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting badge achievements: {e}")
            return Response(
                {"error": "Failed to get badge achievements"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BadgeAchievementViewSet(viewsets.ViewSet):
    """ViewSet for badge achievements and milestones."""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get achievements for the current user."""
        try:
            # Get current user's writer profile
            try:
                writer = WriterProfile.objects.get(user=request.user)
            except WriterProfile.DoesNotExist:
                return Response(
                    {"error": "Writer profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            achievements = BadgeAchievementService.get_writer_achievements(writer)
            return Response(achievements, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting writer achievements: {e}")
            return Response(
                {"error": "Failed to get achievements"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def milestones(self, request):
        """Get next milestones for the current user."""
        try:
            # Get current user's writer profile
            try:
                writer = WriterProfile.objects.get(user=request.user)
            except WriterProfile.DoesNotExist:
                return Response(
                    {"error": "Writer profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            milestones = BadgeAchievementService.get_next_milestones(writer)
            return Response(milestones, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting milestones: {e}")
            return Response(
                {"error": "Failed to get milestones"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get achievement leaderboard."""
        try:
            achievement_type = request.query_params.get('type', 'badge_milestone')
            limit = int(request.query_params.get('limit', 10))
            leaderboard = BadgeAchievementService.get_achievement_leaderboard(achievement_type, limit)
            return Response(leaderboard, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting achievement leaderboard: {e}")
            return Response(
                {"error": "Failed to get achievement leaderboard"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall achievement statistics."""
        try:
            stats = BadgeAchievementService.get_achievement_statistics()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting achievement statistics: {e}")
            return Response(
                {"error": "Failed to get achievement statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BadgePerformanceViewSet(viewsets.ViewSet):
    """ViewSet for individual writer badge performance."""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get badge performance for the current user."""
        try:
            # Get current user's writer profile
            try:
                writer = WriterProfile.objects.get(user=request.user)
            except WriterProfile.DoesNotExist:
                return Response(
                    {"error": "Writer profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            performance = BadgeAnalyticsService.get_writer_badge_performance(writer.id)
            if not performance:
                return Response(
                    {"error": "Performance data not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(performance, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting writer badge performance: {e}")
            return Response(
                {"error": "Failed to get writer badge performance"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """Get badge performance for a specific writer."""
        try:
            # Check if user is admin or requesting their own data
            if not request.user.is_staff and str(request.user.writer_profile.id) != pk:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            performance = BadgeAnalyticsService.get_writer_badge_performance(int(pk))
            if not performance:
                return Response(
                    {"error": "Writer not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(performance, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting writer badge performance: {e}")
            return Response(
                {"error": "Failed to get writer badge performance"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def achievements(self, request, pk=None):
        """Get achievements for a specific writer."""
        try:
            # Check if user is admin or requesting their own data
            if not request.user.is_staff and str(request.user.writer_profile.id) != pk:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                writer = WriterProfile.objects.get(id=pk)
            except WriterProfile.DoesNotExist:
                return Response(
                    {"error": "Writer not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            achievements = BadgeAchievementService.get_writer_achievements(writer)
            return Response(achievements, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting writer achievements: {e}")
            return Response(
                {"error": "Failed to get writer achievements"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

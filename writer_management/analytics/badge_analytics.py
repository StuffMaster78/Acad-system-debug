# writer_management/analytics/badge_analytics.py

from django.db.models import Count, Q, F, Avg, Max, Min
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from writer_management.models.badges import Badge, WriterBadge
from writer_management.models.profile import WriterProfile
from writer_management.models.metrics import WriterPerformanceMetrics
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BadgeAnalyticsService:
    """Service for badge analytics and insights."""
    
    @staticmethod
    def get_badge_distribution() -> Dict[str, Any]:
        """Get distribution of badges across all writers."""
        try:
            # Get badge counts
            badge_counts = WriterBadge.objects.filter(
                revoked=False
            ).values('badge__name', 'badge__icon', 'badge__type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Get total writers with badges
            total_writers_with_badges = WriterBadge.objects.filter(
                revoked=False
            ).values('writer').distinct().count()
            
            # Get total badges awarded
            total_badges_awarded = WriterBadge.objects.filter(revoked=False).count()
            
            return {
                'badge_distribution': list(badge_counts),
                'total_writers_with_badges': total_writers_with_badges,
                'total_badges_awarded': total_badges_awarded,
                'average_badges_per_writer': total_badges_awarded / total_writers_with_badges if total_writers_with_badges > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting badge distribution: {e}")
            return {}
    
    @staticmethod
    def get_badge_trends(days: int = 30) -> Dict[str, Any]:
        """Get badge awarding trends over time."""
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Get daily badge awards
            daily_awards = WriterBadge.objects.filter(
                issued_at__gte=start_date,
                issued_at__lte=end_date
            ).extra(
                select={'day': 'date(issued_at)'}
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            # Get badge type trends
            type_trends = WriterBadge.objects.filter(
                issued_at__gte=start_date,
                issued_at__lte=end_date
            ).values('badge__type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'daily_awards': list(daily_awards),
                'type_trends': list(type_trends),
                'period_days': days,
                'total_awards_in_period': sum(item['count'] for item in daily_awards)
            }
        except Exception as e:
            logger.error(f"Error getting badge trends: {e}")
            return {}
    
    @staticmethod
    def get_writer_badge_performance(writer_id: int) -> Dict[str, Any]:
        """Get badge performance for a specific writer."""
        try:
            writer = WriterProfile.objects.get(id=writer_id)
            
            # Get writer's badges
            writer_badges = WriterBadge.objects.filter(
                writer=writer,
                revoked=False
            ).select_related('badge')
            
            # Get badge statistics
            total_badges = writer_badges.count()
            badge_types = writer_badges.values('badge__type').annotate(
                count=Count('id')
            )
            
            # Get recent badges (last 30 days)
            recent_badges = writer_badges.filter(
                issued_at__gte=timezone.now() - timedelta(days=30)
            ).count()
            
            # Get performance metrics
            try:
                metrics = writer.performance_metrics
                performance_data = {
                    'total_earned': getattr(metrics, 'total_earned_usd', 0),
                    'completed_orders': getattr(metrics, 'completed_orders', 0),
                    'dispute_rate': getattr(metrics, 'dispute_rate', 0),
                    'top_10_streak_weeks': getattr(metrics, 'top_10_streak_weeks', 0),
                }
            except:
                performance_data = {}
            
            return {
                'writer_id': writer_id,
                'writer_name': writer.user.get_full_name() or writer.user.username,
                'total_badges': total_badges,
                'badge_types': list(badge_types),
                'recent_badges': recent_badges,
                'performance_data': performance_data,
                'badges': [
                    {
                        'name': wb.badge.name,
                        'icon': wb.badge.icon,
                        'type': wb.badge.type,
                        'awarded_at': wb.issued_at.isoformat(),
                        'is_auto': wb.is_auto_awarded
                    }
                    for wb in writer_badges
                ]
            }
        except Exception as e:
            logger.error(f"Error getting writer badge performance: {e}")
            return {}
    
    @staticmethod
    def get_badge_leaderboard(badge_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get badge leaderboard."""
        try:
            # Base query
            query = WriterBadge.objects.filter(revoked=False)
            
            if badge_type:
                query = query.filter(badge__type=badge_type)
            
            # Get writers with badge counts
            leaderboard = query.values(
                'writer__id',
                'writer__user__username',
                'writer__user__first_name',
                'writer__user__last_name'
            ).annotate(
                badge_count=Count('id'),
                latest_badge=Max('issued_at')
            ).order_by('-badge_count', '-latest_badge')[:limit]
            
            # Format results
            result = []
            for i, writer in enumerate(leaderboard, 1):
                result.append({
                    'rank': i,
                    'writer_id': writer['writer__id'],
                    'writer_name': f"{writer['writer__user__first_name']} {writer['writer__user__last_name']}".strip() or writer['writer__user__username'],
                    'badge_count': writer['badge_count'],
                    'latest_badge': writer['latest_badge'].isoformat() if writer['latest_badge'] else None
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting badge leaderboard: {e}")
            return []
    
    @staticmethod
    def get_badge_achievements() -> Dict[str, Any]:
        """Get badge achievement statistics."""
        try:
            # Get total badges
            total_badges = Badge.objects.filter(is_active=True).count()
            
            # Get total awards
            total_awards = WriterBadge.objects.filter(revoked=False).count()
            
            # Get auto vs manual awards
            auto_awards = WriterBadge.objects.filter(
                revoked=False,
                is_auto_awarded=True
            ).count()
            
            manual_awards = WriterBadge.objects.filter(
                revoked=False,
                is_auto_awarded=False
            ).count()
            
            # Get badge types distribution
            type_distribution = Badge.objects.filter(
                is_active=True
            ).values('type').annotate(
                count=Count('id')
            )
            
            # Get recent achievements (last 7 days)
            recent_achievements = WriterBadge.objects.filter(
                issued_at__gte=timezone.now() - timedelta(days=7),
                revoked=False
            ).count()
            
            return {
                'total_badges': total_badges,
                'total_awards': total_awards,
                'auto_awards': auto_awards,
                'manual_awards': manual_awards,
                'type_distribution': list(type_distribution),
                'recent_achievements': recent_achievements,
                'award_rate': auto_awards / total_awards if total_awards > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting badge achievements: {e}")
            return {}
    
    @staticmethod
    def get_badge_insights() -> Dict[str, Any]:
        """Get comprehensive badge insights."""
        try:
            # Get all analytics data
            distribution = BadgeAnalyticsService.get_badge_distribution()
            trends = BadgeAnalyticsService.get_badge_trends()
            achievements = BadgeAnalyticsService.get_badge_achievements()
            leaderboard = BadgeAnalyticsService.get_badge_leaderboard()
            
            # Calculate insights
            insights = {
                'distribution': distribution,
                'trends': trends,
                'achievements': achievements,
                'leaderboard': leaderboard,
                'insights': {
                    'most_popular_badge': max(distribution.get('badge_distribution', []), key=lambda x: x['count']) if distribution.get('badge_distribution') else None,
                    'growth_rate': BadgeAnalyticsService._calculate_growth_rate(),
                    'engagement_score': BadgeAnalyticsService._calculate_engagement_score(),
                }
            }
            
            return insights
        except Exception as e:
            logger.error(f"Error getting badge insights: {e}")
            return {}
    
    @staticmethod
    def _calculate_growth_rate() -> float:
        """Calculate badge award growth rate."""
        try:
            # Get last 30 days vs previous 30 days
            now = timezone.now()
            last_30_days = WriterBadge.objects.filter(
                issued_at__gte=now - timedelta(days=30),
                revoked=False
            ).count()
            
            previous_30_days = WriterBadge.objects.filter(
                issued_at__gte=now - timedelta(days=60),
                issued_at__lt=now - timedelta(days=30),
                revoked=False
            ).count()
            
            if previous_30_days == 0:
                return 0.0
            
            return ((last_30_days - previous_30_days) / previous_30_days) * 100
        except Exception:
            return 0.0
    
    @staticmethod
    def _calculate_engagement_score() -> float:
        """Calculate badge engagement score."""
        try:
            # Get writers with badges
            writers_with_badges = WriterBadge.objects.filter(
                revoked=False
            ).values('writer').distinct().count()
            
            # Get total writers
            total_writers = WriterProfile.objects.count()
            
            if total_writers == 0:
                return 0.0
            
            return (writers_with_badges / total_writers) * 100
        except Exception:
            return 0.0

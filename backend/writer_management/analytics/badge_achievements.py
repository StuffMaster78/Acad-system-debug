# writer_management/analytics/badge_achievements.py

from django.db.models import Count, Q, F, Avg, Max, Min
from writer_management.models.badges import Badge, WriterBadge
from writer_management.models.profile import WriterProfile
from writer_management.models.metrics import WriterPerformanceMetrics
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BadgeAchievementService:
    """Service for badge achievements and milestone tracking."""
    
    # Achievement milestones
    ACHIEVEMENT_MILESTONES = {
        'first_badge': {'count': 1, 'name': 'First Badge', 'icon': '🎯'},
        'badge_collector': {'count': 5, 'name': 'Badge Collector', 'icon': '🏆'},
        'badge_master': {'count': 10, 'name': 'Badge Master', 'icon': '👑'},
        'badge_legend': {'count': 20, 'name': 'Badge Legend', 'icon': '🌟'},
        'badge_god': {'count': 50, 'name': 'Badge God', 'icon': '⚡'},
    }
    
    # Performance milestones
    PERFORMANCE_MILESTONES = {
        'earnings_100': {'amount': 100, 'name': 'First $100', 'icon': '💰'},
        'earnings_500': {'amount': 500, 'name': 'Half Grand', 'icon': '💵'},
        'earnings_1000': {'amount': 1000, 'name': 'Grand Master', 'icon': '💎'},
        'earnings_5000': {'amount': 5000, 'name': 'High Roller', 'icon': '💸'},
        'earnings_10000': {'amount': 10000, 'name': 'Money Bags', 'icon': '🏦'},
    }
    
    # Order milestones
    ORDER_MILESTONES = {
        'orders_10': {'count': 10, 'name': 'Getting Started', 'icon': '📝'},
        'orders_25': {'count': 25, 'name': 'Steady Writer', 'icon': '✍️'},
        'orders_50': {'count': 50, 'name': 'Pro Writer', 'icon': '📚'},
        'orders_100': {'count': 100, 'name': 'Veteran Writer', 'icon': '📖'},
        'orders_250': {'count': 250, 'name': 'Writing Legend', 'icon': '📜'},
    }
    
    @staticmethod
    def check_badge_achievements(writer: WriterProfile) -> List[Dict[str, Any]]:
        """Check and return badge achievements for a writer."""
        try:
            achievements = []
            
            # Get writer's badge count
            badge_count = WriterBadge.objects.filter(
                writer=writer,
                revoked=False
            ).count()
            
            # Check badge milestones
            for milestone_key, milestone_data in BadgeAchievementService.ACHIEVEMENT_MILESTONES.items():
                if badge_count >= milestone_data['count']:
                    achievement = {
                        'type': 'badge_milestone',
                        'key': milestone_key,
                        'name': milestone_data['name'],
                        'icon': milestone_data['icon'],
                        'count': badge_count,
                        'threshold': milestone_data['count'],
                        'achieved_at': timezone.now().isoformat(),
                        'description': f"You've earned {badge_count} badges!"
                    }
                    achievements.append(achievement)
            
            return achievements
        except Exception as e:
            logger.error(f"Error checking badge achievements: {e}")
            return []
    
    @staticmethod
    def check_performance_achievements(writer: WriterProfile) -> List[Dict[str, Any]]:
        """Check and return performance achievements for a writer."""
        try:
            achievements = []
            
            # Get performance metrics
            try:
                metrics = writer.performance_metrics
                total_earned = getattr(metrics, 'total_earned_usd', 0)
                completed_orders = getattr(metrics, 'completed_orders', 0)
            except:
                return achievements
            
            # Check earnings milestones
            for milestone_key, milestone_data in BadgeAchievementService.PERFORMANCE_MILESTONES.items():
                if total_earned >= milestone_data['amount']:
                    achievement = {
                        'type': 'earnings_milestone',
                        'key': milestone_key,
                        'name': milestone_data['name'],
                        'icon': milestone_data['icon'],
                        'amount': total_earned,
                        'threshold': milestone_data['amount'],
                        'achieved_at': timezone.now().isoformat(),
                        'description': f"You've earned ${total_earned:,.2f}!"
                    }
                    achievements.append(achievement)
            
            # Check order milestones
            for milestone_key, milestone_data in BadgeAchievementService.ORDER_MILESTONES.items():
                if completed_orders >= milestone_data['count']:
                    achievement = {
                        'type': 'orders_milestone',
                        'key': milestone_key,
                        'name': milestone_data['name'],
                        'icon': milestone_data['icon'],
                        'count': completed_orders,
                        'threshold': milestone_data['count'],
                        'achieved_at': timezone.now().isoformat(),
                        'description': f"You've completed {completed_orders} orders!"
                    }
                    achievements.append(achievement)
            
            return achievements
        except Exception as e:
            logger.error(f"Error checking performance achievements: {e}")
            return []
    
    @staticmethod
    def get_writer_achievements(writer: WriterProfile) -> Dict[str, Any]:
        """Get all achievements for a writer."""
        try:
            badge_achievements = BadgeAchievementService.check_badge_achievements(writer)
            performance_achievements = BadgeAchievementService.check_performance_achievements(writer)
            
            # Get writer's current stats
            try:
                metrics = writer.performance_metrics
                stats = {
                    'total_badges': WriterBadge.objects.filter(writer=writer, revoked=False).count(),
                    'total_earned': getattr(metrics, 'total_earned_usd', 0),
                    'completed_orders': getattr(metrics, 'completed_orders', 0),
                    'dispute_rate': getattr(metrics, 'dispute_rate', 0),
                    'top_10_streak_weeks': getattr(metrics, 'top_10_streak_weeks', 0),
                }
            except:
                stats = {
                    'total_badges': 0,
                    'total_earned': 0,
                    'completed_orders': 0,
                    'dispute_rate': 0,
                    'top_10_streak_weeks': 0,
                }
            
            # Get next milestones
            next_milestones = BadgeAchievementService.get_next_milestones(writer)
            
            return {
                'writer_id': writer.id,
                'writer_name': writer.user.get_full_name() or writer.user.username,
                'stats': stats,
                'badge_achievements': badge_achievements,
                'performance_achievements': performance_achievements,
                'next_milestones': next_milestones,
                'total_achievements': len(badge_achievements) + len(performance_achievements)
            }
        except Exception as e:
            logger.error(f"Error getting writer achievements: {e}")
            return {}
    
    @staticmethod
    def get_next_milestones(writer: WriterProfile) -> List[Dict[str, Any]]:
        """Get next milestones for a writer."""
        try:
            next_milestones = []
            
            # Get current stats
            try:
                metrics = writer.performance_metrics
                total_earned = getattr(metrics, 'total_earned_usd', 0)
                completed_orders = getattr(metrics, 'completed_orders', 0)
            except:
                total_earned = 0
                completed_orders = 0
            
            badge_count = WriterBadge.objects.filter(writer=writer, revoked=False).count()
            
            # Find next badge milestone
            for milestone_key, milestone_data in BadgeAchievementService.ACHIEVEMENT_MILESTONES.items():
                if badge_count < milestone_data['count']:
                    next_milestones.append({
                        'type': 'badge_milestone',
                        'key': milestone_key,
                        'name': milestone_data['name'],
                        'icon': milestone_data['icon'],
                        'current': badge_count,
                        'target': milestone_data['count'],
                        'remaining': milestone_data['count'] - badge_count,
                        'description': f"Earn {milestone_data['count'] - badge_count} more badges to unlock {milestone_data['name']}!"
                    })
                    break
            
            # Find next earnings milestone
            for milestone_key, milestone_data in BadgeAchievementService.PERFORMANCE_MILESTONES.items():
                if total_earned < milestone_data['amount']:
                    next_milestones.append({
                        'type': 'earnings_milestone',
                        'key': milestone_key,
                        'name': milestone_data['name'],
                        'icon': milestone_data['icon'],
                        'current': total_earned,
                        'target': milestone_data['amount'],
                        'remaining': milestone_data['amount'] - total_earned,
                        'description': f"Earn ${milestone_data['amount'] - total_earned:,.2f} more to unlock {milestone_data['name']}!"
                    })
                    break
            
            # Find next order milestone
            for milestone_key, milestone_data in BadgeAchievementService.ORDER_MILESTONES.items():
                if completed_orders < milestone_data['count']:
                    next_milestones.append({
                        'type': 'orders_milestone',
                        'key': milestone_key,
                        'name': milestone_data['name'],
                        'icon': milestone_data['icon'],
                        'current': completed_orders,
                        'target': milestone_data['count'],
                        'remaining': milestone_data['count'] - completed_orders,
                        'description': f"Complete {milestone_data['count'] - completed_orders} more orders to unlock {milestone_data['name']}!"
                    })
                    break
            
            return next_milestones
        except Exception as e:
            logger.error(f"Error getting next milestones: {e}")
            return []
    
    @staticmethod
    def get_achievement_leaderboard(achievement_type: str = 'badge_milestone', limit: int = 10) -> List[Dict[str, Any]]:
        """Get achievement leaderboard."""
        try:
            if achievement_type == 'badge_milestone':
                # Get writers with most badges
                leaderboard = WriterBadge.objects.filter(
                    revoked=False
                ).values(
                    'writer__id',
                    'writer__user__username',
                    'writer__user__first_name',
                    'writer__user__last_name'
                ).annotate(
                    badge_count=Count('id')
                ).order_by('-badge_count')[:limit]
                
                result = []
                for i, writer in enumerate(leaderboard, 1):
                    result.append({
                        'rank': i,
                        'writer_id': writer['writer__id'],
                        'writer_name': f"{writer['writer__user__first_name']} {writer['writer__user__last_name']}".strip() or writer['writer__user__username'],
                        'achievement_count': writer['badge_count'],
                        'achievement_type': 'badges'
                    })
                
                return result
            
            elif achievement_type == 'earnings_milestone':
                # Get writers with highest earnings
                writers = WriterProfile.objects.filter(
                    performance_metrics__isnull=False
                ).select_related('performance_metrics').order_by(
                    '-performance_metrics__total_earned_usd'
                )[:limit]
                
                result = []
                for i, writer in enumerate(writers, 1):
                    try:
                        earnings = writer.performance_metrics.total_earned_usd
                        result.append({
                            'rank': i,
                            'writer_id': writer.id,
                            'writer_name': writer.user.get_full_name() or writer.user.username,
                            'achievement_count': earnings,
                            'achievement_type': 'earnings'
                        })
                    except:
                        continue
                
                return result
            
            return []
        except Exception as e:
            logger.error(f"Error getting achievement leaderboard: {e}")
            return []
    
    @staticmethod
    def get_achievement_statistics() -> Dict[str, Any]:
        """Get overall achievement statistics."""
        try:
            # Get total writers
            total_writers = WriterProfile.objects.count()
            
            # Get writers with badges
            writers_with_badges = WriterBadge.objects.filter(
                revoked=False
            ).values('writer').distinct().count()
            
            # Get achievement distribution
            achievement_distribution = {
                'first_badge': WriterBadge.objects.filter(revoked=False).values('writer').distinct().count(),
                'badge_collector': WriterBadge.objects.filter(revoked=False).values('writer').annotate(badge_count=Count('id')).filter(badge_count__gte=5).count(),
                'badge_master': WriterBadge.objects.filter(revoked=False).values('writer').annotate(badge_count=Count('id')).filter(badge_count__gte=10).count(),
                'badge_legend': WriterBadge.objects.filter(revoked=False).values('writer').annotate(badge_count=Count('id')).filter(badge_count__gte=20).count(),
                'badge_god': WriterBadge.objects.filter(revoked=False).values('writer').annotate(badge_count=Count('id')).filter(badge_count__gte=50).count(),
            }
            
            return {
                'total_writers': total_writers,
                'writers_with_badges': writers_with_badges,
                'badge_participation_rate': (writers_with_badges / total_writers * 100) if total_writers > 0 else 0,
                'achievement_distribution': achievement_distribution,
                'total_achievements': sum(achievement_distribution.values())
            }
        except Exception as e:
            logger.error(f"Error getting achievement statistics: {e}")
            return {}

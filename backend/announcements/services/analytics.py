"""
Analytics service for announcements.
"""
from django.db.models import Count, Q, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from announcements.models import Announcement, AnnouncementView

User = get_user_model()


class AnnouncementAnalyticsService:
    """Service for generating announcement analytics."""

    @staticmethod
    def get_engagement_stats(announcement):
        """
        Get engagement statistics for an announcement.

        Args:
            announcement: The announcement

        Returns:
            Dictionary with engagement statistics
        """
        views = AnnouncementView.objects.filter(announcement=announcement)

        # Get target users count
        target_roles = announcement.target_roles or []
        if announcement.broadcast.show_to_all:
            total_users = User.objects.filter(is_active=True).count()
        else:
            total_users = User.objects.filter(
                role__in=target_roles,
                is_active=True
            ).count()

        # Basic stats
        total_views = views.count()
        unique_viewers = views.values('user').distinct().count()
        acknowledged_count = views.filter(acknowledged=True).count()

        # Engagement rate
        engagement_rate = (unique_viewers / total_users * 100) if total_users > 0 else 0

        # Views by role
        views_by_role = {}
        for view in views.select_related('user'):
            role = getattr(view.user, 'role', 'unknown')
            views_by_role[role] = views_by_role.get(role, 0) + 1

        # Views over time (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        views_over_time = views.filter(
            viewed_at__gte=thirty_days_ago
        ).extra(
            select={'date': 'date(viewed_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Get readers list
        readers = views.select_related('user').order_by('-viewed_at')[:100]

        # Non-readers count
        if announcement.broadcast.show_to_all:
            non_readers = User.objects.filter(is_active=True).exclude(
                id__in=views.values_list('user_id', flat=True)
            ).count()
        else:
            non_readers = User.objects.filter(
                role__in=target_roles,
                is_active=True
            ).exclude(
                id__in=views.values_list('user_id', flat=True)
            ).count()

        return {
            'total_views': total_views,
            'unique_viewers': unique_viewers,
            'acknowledged_count': acknowledged_count,
            'engagement_rate': round(engagement_rate, 2),
            'views_by_role': views_by_role,
            'views_over_time': list(views_over_time),
            'readers': readers,
            'non_readers_count': non_readers
        }

    @staticmethod
    def get_user_read_status(announcement):
        """
        Get detailed read status for all users.

        Args:
            announcement: The announcement

        Returns:
            Dictionary with readers and non-readers
        """
        views = AnnouncementView.objects.filter(
            announcement=announcement
        ).select_related('user')

        readers = list(views)
        reader_ids = set(views.values_list('user_id', flat=True))

        # Get non-readers
        target_roles = announcement.target_roles or []
        if announcement.broadcast.show_to_all:
            non_readers = User.objects.filter(
                is_active=True
            ).exclude(id__in=reader_ids)
        else:
            non_readers = User.objects.filter(
                role__in=target_roles,
                is_active=True
            ).exclude(id__in=reader_ids)

        return {
            'readers': readers,
            'non_readers': list(non_readers),
            'readers_count': len(readers),
            'non_readers_count': non_readers.count()
        }


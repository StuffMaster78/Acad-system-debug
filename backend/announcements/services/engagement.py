"""
Engagement tracking service for announcements.
"""
from django.utils import timezone
from django.db.models import Count, Q
from announcements.models import Announcement, AnnouncementView


class EngagementTrackingService:
    """Service for tracking user engagement with announcements."""

    @staticmethod
    def track_view(user, announcement, time_spent=None):
        """
        Track when a user views an announcement.

        Args:
            user: The user viewing the announcement
            announcement: The announcement being viewed
            time_spent: Optional time spent viewing in seconds

        Returns:
            AnnouncementView instance
        """
        view, created = AnnouncementView.objects.get_or_create(
            user=user,
            announcement=announcement,
            defaults={
                'viewed_at': timezone.now(),
                'time_spent': time_spent
            }
        )

        # Update time spent if provided and view already existed
        if not created and time_spent is not None:
            view.time_spent = time_spent
            view.save(update_fields=['time_spent'])

        # Increment view count if this is a new view
        if created:
            # Use F() to avoid race conditions and improve performance
            from django.db.models import F
            from django.core.cache import cache
            Announcement.objects.filter(id=announcement.id).update(view_count=F('view_count') + 1)
            announcement.refresh_from_db()
            
            # Invalidate cache for unread count
            website = getattr(user, 'website', None)
            cache_key = f'announcement_unread_count_{user.id}_{website.id if website else "all"}'
            cache.delete(cache_key)

        return view

    @staticmethod
    def acknowledge(user, announcement):
        """
        Mark an announcement as acknowledged by a user.

        Args:
            user: The user acknowledging
            announcement: The announcement being acknowledged

        Returns:
            AnnouncementView instance
        """
        view, created = AnnouncementView.objects.get_or_create(
            user=user,
            announcement=announcement,
            defaults={
                'viewed_at': timezone.now(),
                'acknowledged': True,
                'acknowledged_at': timezone.now()
            }
        )

        if not created:
            view.acknowledged = True
            view.acknowledged_at = timezone.now()
            view.save(update_fields=['acknowledged', 'acknowledged_at'])

        return view

    @staticmethod
    def has_viewed(user, announcement):
        """Check if user has viewed an announcement."""
        return AnnouncementView.objects.filter(
            user=user,
            announcement=announcement
        ).exists()

    @staticmethod
    def has_acknowledged(user, announcement):
        """Check if user has acknowledged an announcement."""
        return AnnouncementView.objects.filter(
            user=user,
            announcement=announcement,
            acknowledged=True
        ).exists()

    @staticmethod
    def get_user_unread_count(user, website=None):
        """
        Get count of unread announcements for a user.
        Optimized query using Exists subquery for better performance.
        Uses caching to avoid repeated database queries.

        Args:
            user: The user
            website: Optional website filter

        Returns:
            Integer count of unread announcements
        """
        from django.db.models import Exists, OuterRef
        from django.core.cache import cache

        # Cache key based on user and website
        cache_key = f'announcement_unread_count_{user.id}_{website.id if website else "all"}'
        
        # Try to get from cache (5 minute TTL)
        cached_count = cache.get(cache_key)
        if cached_count is not None:
            return cached_count

        # Get announcements visible to user
        now = timezone.now()
        queryset = Announcement.objects.filter(
            broadcast__is_active=True
        ).select_related('broadcast', 'broadcast__website').only('id', 'broadcast')

        if website:
            queryset = queryset.filter(broadcast__website=website)

        # Filter by user's role - only count announcements where:
        # 1. User's role is in target_roles, OR
        # 2. show_to_all is True (for system-wide announcements)
        user_role = getattr(user, 'role', None)
        if user_role:
            # Use exact role matching - user's role must be in target_roles array
            queryset = queryset.filter(
                Q(broadcast__target_roles__contains=[user_role]) |
                Q(broadcast__show_to_all=True)
            )
        else:
            # If no role, only count announcements with show_to_all=True
            queryset = queryset.filter(broadcast__show_to_all=True)

        # Exclude expired (only if expires_at is set)
        queryset = queryset.filter(
            Q(broadcast__expires_at__isnull=True) |
            Q(broadcast__expires_at__gte=now)
        )

        # Use Exists subquery instead of exclude(id__in=...) for better performance
        # This avoids loading all viewed IDs into memory
        viewed_subquery = AnnouncementView.objects.filter(
            user=user,
            announcement=OuterRef('pk')
        ).only('id')
        
        # Count unread (announcements that don't have a view for this user)
        unread_count = queryset.exclude(
            Exists(viewed_subquery)
        ).count()

        # Cache the result for 5 minutes
        cache.set(cache_key, unread_count, 300)

        return unread_count


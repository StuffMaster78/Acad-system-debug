# notifications_system/api/views_counters.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

try:
    from notifications_system.utils.unread_counter import get as get_unread
    from notifications_system.utils.unread_rebuild import rebuild_unread
    from notifications_system.models.notifications import Notification
except ImportError as e:
    logger.warning(f"Failed to import notification utilities: {e}")

class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get unread notification count.
        Optimized for frequent polling - uses caching and graceful error handling.
        """
        from django.core.cache import cache
        
        try:
            user = request.user
            if not user or not user.is_authenticated:
                return Response({"unread_count": 0})
            
            # Try to get website from request or user
            website = getattr(request, "website", None) or getattr(user, "website", None)
            wid = getattr(website, "id", None) if website else None

            # Try to get from cache first (cache for 30 seconds to reduce load and rate limiting)
            cache_key = f'unread_count_{user.id}_{wid or "all"}'
            cached_count = cache.get(cache_key)
            if cached_count is not None:
                return Response({"unread_count": cached_count})

            # Try to get from unread counter cache
            try:
                count = get_unread(user.id, wid)
                if count is not None:
                    # Cache for 30 seconds to reduce rate limiting
                    cache.set(cache_key, count, 30)
                    return Response({"unread_count": count})
            except Exception as cache_error:
                logger.debug(f"Cache error in unread count: {cache_error}")

            # If cache miss or error, try to rebuild
            try:
                count = rebuild_unread(user, website)
                if count is not None:
                    # Cache for 30 seconds to reduce rate limiting
                    cache.set(cache_key, count, 30)
                    return Response({"unread_count": count})
            except Exception as rebuild_error:
                logger.debug(f"Rebuild error in unread count: {rebuild_error}")

            # Fallback: direct database query (optimized with select_related)
            # Include both Notification and CommunicationNotification
            try:
                from notifications_system.models.notifications import Notification
                from communications.models import CommunicationNotification
                
                # Count general notifications
                if website:
                    general_count = Notification.objects.filter(
                        user=user,
                        is_read=False,
                        website=website
                    ).count()
                else:
                    general_count = Notification.objects.filter(
                        user=user,
                        is_read=False
                    ).count()
                
                # Count communication notifications (message notifications)
                comm_count = CommunicationNotification.objects.filter(
                    recipient=user,
                    is_read=False
                ).count()
                
                # Total unread count (both types)
                total_count = general_count + comm_count
                
                # Cache result for 30 seconds to reduce rate limiting
                cache.set(cache_key, total_count or 0, 30)
                return Response({"unread_count": total_count or 0})
            except Exception as db_error:
                logger.error(f"Database error in unread count: {db_error}", exc_info=True)
                # Return cached value if available, otherwise 0
                return Response({"unread_count": 0})

        except Exception as e:
            # Log the error for debugging but return 0 to prevent 500
            logger.error(f"Unexpected error in unread count view: {e}", exc_info=True)
            return Response({"unread_count": 0})

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
        try:
            user = request.user
            if not user or not user.is_authenticated:
                return Response({"unread_count": 0})
            
            # Try to get website from request or user
            website = getattr(request, "website", None) or getattr(user, "website", None)
            wid = getattr(website, "id", None) if website else None

            # Try to get from cache first
            try:
                count = get_unread(user.id, wid)
                if count is not None:
                    return Response({"unread_count": count})
            except Exception as cache_error:
                logger.warning(f"Cache error in unread count: {cache_error}")

            # If cache miss or error, try to rebuild
            try:
                count = rebuild_unread(user, website)
                if count is not None:
                    return Response({"unread_count": count})
            except Exception as rebuild_error:
                logger.warning(f"Rebuild error in unread count: {rebuild_error}")

            # Fallback: direct database query
            try:
                from notifications_system.models.notifications import Notification
                if website:
                    count = Notification.objects.filter(
                        user=user,
                        is_read=False,
                        website=website
                    ).count()
                else:
                    count = Notification.objects.filter(
                        user=user,
                        is_read=False
                    ).count()
                return Response({"unread_count": count or 0})
            except Exception as db_error:
                logger.error(f"Database error in unread count: {db_error}", exc_info=True)
                return Response({"unread_count": 0})

        except Exception as e:
            # Log the error for debugging but return 0 to prevent 500
            logger.error(f"Unexpected error in unread count view: {e}", exc_info=True)
            return Response({"unread_count": 0})

# notifications_system/api/views_feed.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.serializers import NotificationSerializer
from notifications_system.utils.last_seen import set_last_seen, get_last_seen
from notifications_system.utils.unread_counter import get as get_unread
from notifications_system.utils.unread_rebuild import rebuild_unread

class NotificationFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        website = getattr(request, "website", None)  # if you attach tenant to request

        # mark “last seen”
        set_last_seen(user)

        qs = NotificationsUserStatus.objects.select_related("notification") \
            .filter(user=user) \
            .order_by("-pinned", "-notification__created_at")

        if website:
            qs = qs.filter(notification__website=website)

        # simple pagination params
        limit = int(request.GET.get("limit", 25))
        offset = int(request.GET.get("offset", 0))
        page = qs[offset: offset + limit]

        # serialize as notifications (not the status rows)
        serializer = NotificationSerializer(
            [s.notification for s in page],
            many=True,
            context={"request": request},
        )

        # unread count (cached; rebuild if missing)
        wid = getattr(website, "id", None)
        unread = get_unread(user.id, wid)
        if unread is None:
            unread = rebuild_unread(user, website)

        return Response({
            "results": serializer.data,
            "count": qs.count(),
            "unread_count": unread,
            "last_seen_at": getattr(get_last_seen(user), "isoformat", lambda: None)(),
            "fetched_at": timezone.now().isoformat(),
        })
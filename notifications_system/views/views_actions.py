# notifications_system/api/views_actions.py  (append to same file)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404

from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.utils.unread_counter import decr
from notifications_system.utils.unread_counter import set_ as set_unread
from django.db.models import Q
from notifications_system.utils.idempotency import idempotent

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id: int, *args, **kwargs):
        user = request.user
        status = get_object_or_404(
            NotificationsUserStatus,
            user=user,
            notification_id=notification_id,
        )
        if not status.is_read:
            status.is_read = True
            status.read_at = timezone.now()
            status.save(update_fields=["is_read", "read_at"])

            website_id = getattr(getattr(status.notification, "website", None), "id", None)
            decr(user.id, website_id, by=1)

        return Response({"ok": True})

class NotificationBulkMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    # id_key = self.request.headers.get("Idempotency-Key")
    # if id_key and not idempotent(f"bulk_mark:{self.request.user.id}:{id_key}", ttl=120):
    #     return Response({"detail": "Duplicate request ignored"}, status=200)

    def post(self, request, *args, **kwargs):
        user = request.user
        website = getattr(request, "website", None)

        qs = NotificationsUserStatus.objects.filter(user=user, is_read=False)
        if website:
            qs = qs.filter(notification__website=website)

        now = timezone.now()
        updated = qs.update(is_read=True, read_at=now)

        # snap cache to 0 for this tenant scope
        wid = getattr(website, "id", None)
        set_unread(user.id, 0, wid)

        return Response({"ok": True, "updated": updated})
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from notifications_system.models.notifications import Notification
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.serializers import NotificationSerializer
from notifications_system.throttles import NotificationThrottle
from notifications_system.filters import NotificationFilter
from notifications_system.throttles import (
    NotificationWriteBurstThrottle, NotificationWriteSustainedThrottle
)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles listing and interacting with user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [NotificationThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

    # def get_queryset(self):
    #     return Notification.objects.filter(
    #         user=self.request.user,
    #         website=self.request.user.website
    #     ).order_by("-created_at")


    def get_queryset(self):
        qs = Notification.objects.all().select_related("user").prefetch_related("user_statuses")
        # lock results to the current user for user-facing endpoints
        if not self.request.user.is_staff:
            qs = qs.filter(user_statuses__user=self.request.user)

        # ensure distinct if any relation-based filters are used
        params = self.request.query_params
        if any(k in params for k in ("is_read", "is_acknowledged", "pinned", "user_id")):
            qs = qs.distinct()
        return qs
    

    @action(detail=False, methods=["get"])
    def unread(self, request):
        qs = self.get_queryset().filter(is_read=False)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get unread count including both Notification and CommunicationNotification."""
        from communications.models import CommunicationNotification

        cache_key = f"notifications:unread_count:{request.user.id}"
        cached_count = cache.get(cache_key)
        if cached_count is not None:
            return Response({"unread_count": cached_count})

        # Count general notifications (use per-user status table when applicable)
        if request.user.is_staff:
            general_count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        else:
            general_count = NotificationsUserStatus.objects.filter(
                user=request.user,
                is_read=False
            ).count()

        # Count communication notifications (message notifications)
        comm_count = CommunicationNotification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        # Total unread count
        total_count = general_count + comm_count
        cache.set(cache_key, total_count, timeout=10)
        return Response({"unread_count": total_count})

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        cache.delete(f"notifications:unread_count:{request.user.id}")
        return Response(
            {"status": "marked as read"}
        )

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        count = self.get_queryset().filter(is_read=False).update(is_read=True)
        cache.delete(f"notifications:unread_count:{request.user.id}")
        return Response(
            {"status": "all marked as read",
             "updated": count}
        )

class NotificationStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [
        NotificationWriteBurstThrottle,
        NotificationWriteSustainedThrottle
    ]

    def get_queryset(self):
        # Always scope to the current user
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            website=self.request.user.website
        ).order_by("-created_at")


class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationAsReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        Mark a notification as read.
        """
        pk = kwargs.get("pk")
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"status": "read"})
        except Notification.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


    def get_queryset(self):
        """
        Optionally filter notifications by read status.
        """
        qs = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == "true")
        return qs.order_by("-created_at")

class UnreadNotificationCountView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get total unread count including both Notification and CommunicationNotification."""
        try:
            from communications.models import CommunicationNotification
            
            website = getattr(request.user, 'website', None)
            
            # Count general notifications
            if website:
                general_count = Notification.objects.filter(
                    user=request.user,
                    is_read=False,
                    website=website
                ).count()
            else:
                # If user has no website, count all unread notifications
                general_count = Notification.objects.filter(
                    user=request.user,
                    is_read=False
                ).count()
            
            # Count communication notifications (message notifications)
            comm_count = CommunicationNotification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
            
            # Total unread count (both types)
            total_count = general_count + comm_count
            return Response({"unread_count": total_count})
        except Exception as e:
            # Return 0 on any error to prevent 500
            return Response({"unread_count": 0})
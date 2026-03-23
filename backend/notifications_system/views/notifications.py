"""
Notification feed, read state, pin state, and unread count.
"""
from __future__ import annotations

import logging
from typing import Any, cast

from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from notifications_system.models.notifications import Notification
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.serializers import (
    NotificationSerializer,
    NotificationListSerializer,
)
from notifications_system.services.inapp_service import InAppService
from notifications_system.throttles import NotificationMarkReadThrottle

logger = logging.getLogger(__name__)


class NotificationFeedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Notification feed for the authenticated user.

    list   → paginated feed (lightweight serializer)
    detail → full notification with all fields
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> type:
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer

    def get_queryset(self) -> QuerySet:  # type: ignore[override]
        request = cast(Request, self.request)
        user = request.user
        website = getattr(user, 'website', None)
        qs = InAppService.get_feed(user, website)
        
        # Validate queryset
        if qs is None:
            return Notification.objects.none()

        # Filter by category
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        # Filter by read state
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            should_be_read = is_read.lower() == 'true'
            status_ids = NotificationsUserStatus.objects.filter(
                user=user,
                website=website,
                is_read=should_be_read,
            ).values_list('notification_id', flat=True)
            qs = qs.filter(id__in=status_ids)

        # Filter by priority
        priority = request.query_params.get('priority')
        if priority:
            qs = qs.filter(priority=priority)

        # Filter by event_key
        event_key = request.query_params.get('event_key')
        if event_key:
            qs = qs.filter(event_key__icontains=event_key)

        return qs

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # Touch last_seen_at when user opens the feed
        website = getattr(request.user, 'website', None)
        InAppService.touch(request.user, website)
        return super().list(request, *args, **kwargs)

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        # Pre-warm the user status cache for list serializer
        if self.action == 'list':
            self._warm_status_cache(context)
        return context

    def _warm_status_cache(self, context: dict[str, Any]) -> None:
        """
        Pre-fetch all NotificationsUserStatus rows for the current page
        so the serializer does not fire N+1 queries.
        """
        request = cast(Request, context.get('request'))
        if not request:
            return
        if not hasattr(request, '_notif_status_cache'):
            # Get the current page's notifications
            page = getattr(self, 'page', None)
            if page:
                notification_ids = [n.id for n in page]
                statuses = NotificationsUserStatus.objects.filter(
                    notification_id__in=notification_ids,
                    user=request.user,
                    website=getattr(request.user, 'website', None),
                )
                # Cache by notification_id for O(1) lookup in serializer
                request._notif_status_cache = {s.notification.id: s for s in statuses}  # type: ignore[attr-defined]

    @action(detail=False, methods=['get'])
    def unread_count(self, request: Request) -> Response:
        """Return cached unread count. Used by the bell icon."""
        website = getattr(request.user, 'website', None)
        count = InAppService.get_unread_count(request.user, website)
        return Response({'unread_count': count})

    @action(
        detail=True,
        methods=['patch'],
        throttle_classes=[NotificationMarkReadThrottle],
    )
    def mark_read(self, request: Request, pk: int = 0) -> Response:
        """Mark a single notification as read."""
        website = getattr(request.user, 'website', None)
        found = InAppService.mark_read(request.user, website, pk)
        if not found:
            return Response(
                {'error': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'status': 'read'})

    @action(detail=False, methods=['patch'])
    def mark_all_read(self, request: Request) -> Response:
        """Mark all unread notifications as read."""
        website = getattr(request.user, 'website', None)
        updated = InAppService.mark_all_read(request.user, website)
        return Response({'marked_read': updated})

    @action(detail=True, methods=['patch'])
    def pin(self, request: Request, pk: int = 0) -> Response:
        """Pin a notification."""
        website = getattr(request.user, 'website', None)
        found = InAppService.pin(request.user, website, pk)
        if not found:
            return Response(
                {'error': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'status': 'pinned'})

    @action(detail=True, methods=['patch'])
    def unpin(self, request: Request, pk: int = 0) -> Response:
        """Unpin a notification."""
        website = getattr(request.user, 'website', None)
        found = InAppService.unpin(request.user, website, pk)
        if not found:
            return Response(
                {'error': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'status': 'unpinned'})

    @action(detail=True, methods=['patch'])
    def acknowledge(self, request: Request, pk: int = 0) -> Response:
        """Acknowledge a critical or action-required notification."""
        website = getattr(request.user, 'website', None)
        found = InAppService.acknowledge(request.user, website, pk)
        if not found:
            return Response(
                {'error': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'status': 'acknowledged'})

    @action(detail=False, methods=['get'])
    def pinned(self, request: Request) -> Response:
        """Return all pinned notifications."""
        website = getattr(request.user, 'website', None)
        queryset = InAppService.get_pinned(request.user, website)
        if queryset is None:
            queryset = Notification.objects.none()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def critical(self, request: Request) -> Response:
        """Return unread critical notifications."""
        website = getattr(request.user, 'website', None)
        queryset = InAppService.get_critical(request.user, website)
        if queryset is None:
            queryset = Notification.objects.none()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
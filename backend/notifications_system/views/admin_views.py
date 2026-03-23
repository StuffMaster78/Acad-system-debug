from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional, cast

from django.db.models import QuerySet
from django.utils.dateparse import parse_datetime
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from notifications_system.enums import NotificationPriority
from notifications_system.models.delivery import Delivery
from notifications_system.models.notification_log import NotificationLog
from notifications_system.serializers import (
    BroadcastNotificationSerializer,
    DeliverySerializer,
    NotificationLogSerializer,
    NotificationPreferenceProfileSerializer,
)
from notifications_system.services.broadcast_services import BroadcastService
from notifications_system.services.notification_profile_service import (
    NotificationProfileService,
)

logger = logging.getLogger(__name__)


def _parse_datetime(value: Any) -> Optional[datetime]:
    """
    Parse a datetime value from request data.
    Accepts datetime instances, ISO strings, or None.
    Returns None if unparseable.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        parsed = parse_datetime(value)
        if parsed is None:
            logger.warning("_parse_datetime: could not parse %r.", value)
        return parsed
    return None


class AdminBroadcastViewSet(viewsets.ViewSet):
    """
    Admin endpoints for creating and managing broadcasts.
    Requires IsAdmin permission.
    """

    def get_permissions(self):
        from admin_management.permissions import IsAdmin
        return [IsAdmin()]

    @action(detail=False, methods=['post'])
    def send(self, request: Request):
        """Create and fan out a broadcast to users on this website."""
        website = getattr(request.user, 'website', None)
        data: dict[str, Any] = cast(dict[str, Any], request.data)

        required = {'event_key', 'title', 'message'}
        missing = required - set(data.keys())
        if missing:
            return Response(
                {'error': f"Missing required fields: {missing}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        channels = data.get('channels')
        target_roles = data.get('target_roles')

        broadcast = BroadcastService.send_broadcast(
            event_key=str(data.get('event_key', '')),
            title=str(data.get('title', '')),
            message=str(data.get('message', '')),
            website=website,
            channels=list(channels) if isinstance(channels, list) else None,
            target_roles=list(target_roles) if isinstance(target_roles, list) else None,
            show_to_all=bool(data.get('show_to_all', False)),
            triggered_by=request.user,
            priority=str(data.get('priority', NotificationPriority.NORMAL)),
            is_critical=bool(data.get('is_critical', False)),
            is_blocking=bool(data.get('is_blocking', False)),
            require_acknowledgement=bool(data.get('require_acknowledgement', False)),
            scheduled_for=_parse_datetime(data.get('scheduled_for')),   # ← Bug 5
            expires_at=_parse_datetime(data.get('expires_at')),         # ← Bug 5
        )
        return Response(
            {
                'broadcast_id': broadcast.pk,
                'status': 'queued',
                'broadcast': BroadcastNotificationSerializer(broadcast).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def preview(self, request: Request, pk=None):
        """Send a preview broadcast to the requesting admin only."""
        data: dict[str, Any] = cast(dict[str, Any], request.data)
        BroadcastService.preview_to_user(
            event_key=str(data.get('event_key', 'system.broadcast')),
            title=str(data.get('title', 'Preview')),
            message=str(data.get('message', '')),
            user=request.user,
            website=getattr(request.user, 'website', None),
            triggered_by=request.user,
        )
        return Response({'status': 'preview sent to your account'})

    @action(detail=True, methods=['post'])
    def cancel(self, request: Request, pk=None):
        """Cancel a scheduled broadcast before it fires."""
        # Bug 2 fix — pk comes as str | None from DRF, cast safely
        if not pk:
            return Response(
                {'error': 'broadcast id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            broadcast_id = int(pk)
        except (TypeError, ValueError):
            return Response(
                {
                    'error': 'broadcast id must be an integer.',
                    'received': str(pk),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cancelled = BroadcastService.cancel_broadcast(
            broadcast_id=broadcast_id,
            cancelled_by=request.user,
        )
        if not cancelled:
            return Response(
                {'error': 'Broadcast not found or already sent.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'status': 'cancelled'})

    @action(detail=False, methods=['get'])
    def list_all(self, request: Request):
        """List all broadcasts for this website with status."""
        from notifications_system.models.broadcast_notification import (
            BroadcastNotification,
        )
        website = getattr(request.user, 'website', None)
        broadcasts = BroadcastNotification.objects.filter(
            website=website,
        ).order_by('-created_at')
        return Response(
            BroadcastNotificationSerializer(
                broadcasts,
                many=True,
                context={'request': request},
            ).data
        )


class AdminNotificationProfileViewSet(viewsets.ViewSet):
    """
    Admin endpoints for managing notification preference profiles.
    Profiles are templates that can be applied to users in bulk.
    """

    def get_permissions(self):
        from admin_management.permissions import IsAdmin
        return [IsAdmin()]

    def list(self, request: Request):
        """List all preference profiles for this website."""
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )
        website = getattr(request.user, 'website', None)
        profiles = NotificationPreferenceProfile.objects.filter(
            website=website,
            is_active=True,
        ).order_by('-is_default', 'name')
        return Response(
            NotificationPreferenceProfileSerializer(profiles, many=True).data
        )

    @action(detail=False, methods=['post'])
    def create_profile(self, request: Request):
        """Create a new notification preference profile."""
        website = getattr(request.user, 'website', None)
        data: dict[str, Any] = cast(dict[str, Any], request.data)

        if not data.get('name'):
            return Response(
                {'error': 'name is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = NotificationProfileService.create_profile(
            name=str(data.get('name', '')),
            website=website,
            description=str(data.get('description', '')),
            email_enabled=bool(data.get('email_enabled', True)),
            in_app_enabled=bool(data.get('in_app_enabled', True)),
            dnd_enabled=bool(data.get('dnd_enabled', False)),
            dnd_start_hour=int(data.get('dnd_start_hour', 22)),
            dnd_end_hour=int(data.get('dnd_end_hour', 6)),
            digest_enabled=bool(data.get('digest_enabled', False)),
            is_default=bool(data.get('is_default', False)),
            created_by=request.user,
        )
        return Response(
            NotificationPreferenceProfileSerializer(profile).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def apply_to_user(self, request: Request, pk=None):
        """
        Apply a preference profile to a single user.

        Body:
            user_id           int   required
            override_existing bool  optional — default False
        """
        from django.contrib.auth import get_user_model
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )
        User = get_user_model()
        data: dict[str, Any] = cast(dict[str, Any], request.data)

        try:
            profile = NotificationPreferenceProfile.objects.get(id=pk)
        except NotificationPreferenceProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_id = data.get('user_id')
        if user_id is None:
            return Response(
                {
                    'error': 'user_id is required.',
                    'detail': (
                        'Provide the ID of the user to apply '
                        'this profile to in the request body.'
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return Response(
                {
                    'error': 'user_id must be an integer.',
                    'received': str(user_id),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': f"User with id={user_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        website = getattr(request.user, 'website', None)
        if (
            getattr(request.user, 'role', '') != 'superadmin'
            and website
            and getattr(user, 'website', None) != website
        ):
            return Response(
                {
                    'error': (
                        'You can only apply profiles to users '
                        'on your website.'
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        result = NotificationProfileService.apply_profile_to_user(
            profile=profile,
            user=user,
            website=website,
            override_existing=bool(data.get('override_existing', False)),
        )
        return Response(result)

    @action(detail=True, methods=['post'])
    def apply_to_users(self, request: Request, pk=None):
        """
        Apply a preference profile to multiple specific users.

        Body:
            user_ids          list[int]  required
            override_existing bool       optional — default False
        """
        from django.contrib.auth import get_user_model
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )
        User = get_user_model()
        data: dict[str, Any] = cast(dict[str, Any], request.data)

        try:
            profile = NotificationPreferenceProfile.objects.get(id=pk)
        except NotificationPreferenceProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_ids = data.get('user_ids')
        if not user_ids:
            return Response(
                {
                    'error': 'user_ids is required.',
                    'detail': 'Pass a list of user IDs e.g. {"user_ids": [1, 2, 3]}',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(user_ids, list):
            return Response(
                {
                    'error': 'user_ids must be a list.',
                    'received': type(user_ids).__name__,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_ids = [int(uid) for uid in user_ids]
        except (TypeError, ValueError):
            return Response(
                {'error': 'All values in user_ids must be integers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        website = getattr(request.user, 'website', None)

        filter_kwargs: dict[str, Any] = {'id__in': user_ids}
        if getattr(request.user, 'role', '') != 'superadmin' and website:
            filter_kwargs['website'] = website

        valid_ids = list(
            User.objects.filter(**filter_kwargs).values_list('id', flat=True)
        )
        not_found = [uid for uid in user_ids if uid not in valid_ids]

        # Bug 3 fix — build result dict explicitly rather than mutating
        service_result = NotificationProfileService.apply_profile_to_users(
            profile=profile,
            website=website,
            user_ids=valid_ids,
            override_existing=bool(data.get('override_existing', False)),
        )
        result: dict[str, Any] = {
            **service_result,
            'not_found': not_found,
            'total_requested': len(user_ids),
        }
        return Response(result)

    @action(detail=True, methods=['post'])
    def apply_to_role(self, request: Request, pk=None):
        """
        Apply a preference profile to all users of a role on this website.

        Body:
            role              str   required — e.g. 'writer', 'client'
            override_existing bool  optional — default False
        """
        from django.contrib.auth import get_user_model
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )
        User = get_user_model()
        data: dict[str, Any] = cast(dict[str, Any], request.data)

        try:
            profile = NotificationPreferenceProfile.objects.get(id=pk)
        except NotificationPreferenceProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        role = data.get('role')
        if not role:
            return Response(
                {
                    'error': 'role is required.',
                    'detail': (
                        'Provide the role to apply this profile to '
                        'e.g. "writer", "client", "support".'
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(role, str) or not role.strip():
            return Response(
                {'error': 'role must be a non-empty string.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        website = getattr(request.user, 'website', None)

        users = User.objects.filter(
            role=role.strip(),
            is_active=True,
            website=website,
        )

        if not users.exists():
            return Response(
                {
                    'error': (
                        f"No active users found with "
                        f"role='{role.strip()}' on this website."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        user_ids = list(users.values_list('id', flat=True))

        result = NotificationProfileService.apply_profile_to_users(
            profile=profile,
            website=website,
            user_ids=user_ids,
            override_existing=bool(data.get('override_existing', False)),
        )
        return Response(result)

    @action(detail=True, methods=['get'])
    def statistics(self, request: Request, pk=None):
        """Profile usage statistics."""
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )
        try:
            profile = NotificationPreferenceProfile.objects.get(id=pk)
        except NotificationPreferenceProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            NotificationProfileService.get_profile_statistics(profile)
        )


class AdminDeliveryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin view of delivery attempts for debugging.
    Superadmin only.
    """
    serializer_class = DeliverySerializer

    def get_permissions(self):
        from admin_management.permissions import IsSuperAdmin
        return [IsSuperAdmin()]

    def get_queryset(self) -> QuerySet:  # type: ignore[override]
        request: Request = self.request  # type: ignore[assignment]
        website = getattr(request.user, 'website', None)
        qs = Delivery.objects.filter(
            website=website,
        ).order_by('-queued_at')

        user_id = request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)

        channel = request.query_params.get('channel')
        if channel:
            qs = qs.filter(channel=channel)

        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        event_key = request.query_params.get('event_key')
        if event_key:
            qs = qs.filter(event_key=event_key)

        return qs


class AdminNotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Immutable audit trail of all delivery attempts.
    Superadmin only.
    """
    serializer_class = NotificationLogSerializer

    def get_permissions(self):
        from admin_management.permissions import IsSuperAdmin
        return [IsSuperAdmin()]

    def get_queryset(self) -> QuerySet:  # type: ignore[override]
        request: Request = self.request  # type: ignore[assignment]
        website = getattr(request.user, 'website', None)
        qs = NotificationLog.objects.filter(
            website=website,
        ).order_by('-attempted_at')

        user_id = request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)

        return qs
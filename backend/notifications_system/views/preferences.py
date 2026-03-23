"""
User notification preference management.
Users control channel toggles, DND, digest, and per-event settings.
"""
from __future__ import annotations

import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications_system.serializers import (
    NotificationPreferenceSerializer,
    NotificationEventPreferenceSerializer,
)
from notifications_system.services.preference_service import PreferenceService
from notifications_system.throttles import NotificationPreferenceUpdateThrottle

logger = logging.getLogger(__name__)

# Fields the user is allowed to update on their master preference
UPDATABLE_PREFERENCE_FIELDS = {
    'email_enabled',
    'in_app_enabled',
    'dnd_enabled',
    'dnd_start_hour',
    'dnd_end_hour',
    'mute_all',
    'mute_until',
    'digest_enabled',
    'digest_only',
    'digest_frequency',
    'min_priority',
}

# Fields the user is allowed to update on per-event preferences
UPDATABLE_EVENT_PREF_FIELDS = {
    'email_enabled',
    'in_app_enabled',
    'digest_enabled',
    'is_enabled',
}


class NotificationPreferenceView(APIView):
    """
    GET  /notifications/preferences/    → return current preferences
    PATCH /notifications/preferences/   → update specific fields
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [NotificationPreferenceUpdateThrottle]

    def get(self, request):
        website = getattr(request.user, 'website', None)
        pref = PreferenceService.get_or_create_preference(
            request.user, website
        )
        return Response(NotificationPreferenceSerializer(pref).data)

    def patch(self, request):
        website = getattr(request.user, 'website', None)
        updates = {
            k: v for k, v in request.data.items()
            if k in UPDATABLE_PREFERENCE_FIELDS
        }
        if not updates:
            return Response(
                {'error': 'No valid fields provided.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        PreferenceService.update_preference(request.user, website, **updates)
        pref = PreferenceService.get_or_create_preference(
            request.user, website
        )
        return Response(NotificationPreferenceSerializer(pref).data)


class NotificationEventPreferenceViewSet(viewsets.ViewSet):
    """
    Per-event preference management.
    Users toggle individual event types on/off per channel.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List all per-event preferences grouped by category."""
        from notifications_system.models.notification_preferences import (
            NotificationEventPreference,
        )
        website = getattr(request.user, 'website', None)
        prefs = NotificationEventPreference.objects.filter(
            user=request.user,
            website=website,
        ).select_related('event').order_by('event__category', 'event__event_key')

        # Group by category for the UI
        group_by = request.query_params.get('group_by') == 'category'
        if group_by:
            grouped = {}
            for pref in prefs:
                cat = pref.event.category or 'other'
                grouped.setdefault(cat, []).append(pref)
            return Response({
                cat: NotificationEventPreferenceSerializer(items, many=True).data
                for cat, items in grouped.items()
            })

        return Response(
            NotificationEventPreferenceSerializer(prefs, many=True).data
        )

    def partial_update(self, request, pk=None):
        """Update a specific event preference."""
        from notifications_system.models.notification_preferences import (
            NotificationEventPreference,
        )
        website = getattr(request.user, 'website', None)
        try:
            pref = NotificationEventPreference.objects.get(
                id=pk, user=request.user, website=website,
            )
        except NotificationEventPreference.DoesNotExist:
            return Response(
                {'error': 'Event preference not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        updates = {
            k: v for k, v in request.data.items()
            if k in UPDATABLE_EVENT_PREF_FIELDS
        }
        for field, value in updates.items():
            setattr(pref, field, value)
        pref.save(update_fields=list(updates.keys()) + ['updated_at'])
        PreferenceService._invalidate_cache(request.user, website)

        return Response(NotificationEventPreferenceSerializer(pref).data)

    @action(detail=False, methods=['post'])
    def reset(self, request):
        """Reset all preferences to system defaults."""
        website = getattr(request.user, 'website', None)
        PreferenceService.reset_preferences(request.user, website)
        return Response({'status': 'preferences reset to defaults'})

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update multiple event preferences at once.
        Body: [{"id": 1, "email_enabled": false}, ...]
        """
        from notifications_system.models.notification_preferences import (
            NotificationEventPreference,
        )
        website = getattr(request.user, 'website', None)
        items = request.data if isinstance(request.data, list) else []

        updated = 0
        errors = []
        for item in items:
            pref_id = item.get('id')
            if not pref_id:
                continue
            try:
                pref = NotificationEventPreference.objects.get(
                    id=pref_id, user=request.user, website=website,
                )
                updates = {
                    k: v for k, v in item.items()
                    if k in UPDATABLE_EVENT_PREF_FIELDS
                }
                for field, value in updates.items():
                    setattr(pref, field, value)
                pref.save(update_fields=list(updates.keys()) + ['updated_at'])
                updated += 1
            except NotificationEventPreference.DoesNotExist:
                errors.append(pref_id)

        PreferenceService._invalidate_cache(request.user, website)
        return Response({'updated': updated, 'not_found': errors})
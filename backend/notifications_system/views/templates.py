"""
Template management — admin and superadmin.
"""
from __future__ import annotations

import logging
from typing import cast

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import QuerySet


from notifications_system.models.notifications_template import NotificationTemplate
from notifications_system.models.notification_event import (
    NotificationEvent as NotificationEventModel,
)
from notifications_system.serializers import (
    NotificationTemplateSerializer,
    NotificationTemplateCreateSerializer,
    NotificationEventSerializer,
    NotificationEventConfigSerializer,
)
from notifications_system.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    Manage notification templates.
    Superadmin: manages global templates (website=null).
    Admin: manages website-specific overrides.
    """

    def get_permissions(self):
        from admin_management.permissions import IsAdmin
        return [IsAdmin()]

    def get_queryset(self) -> QuerySet:  # type: ignore[override]
        from django.db.models import Q
        request = cast(Request, self.request)
        user = request.user
        website = getattr(user, 'website', None)

        qs = NotificationTemplate.objects.select_related(
            'event', 'website'
        )

        if getattr(user, 'role', '') == 'superadmin':
            website_filter = request.query_params.get('website')
            if website_filter:
                qs = qs.filter(website_id=website_filter)
        else:
            qs = qs.filter(
                Q(website=website) | Q(website__isnull=True)
            )

        channel = request.query_params.get('channel')
        if channel:
            qs = qs.filter(channel=channel)

        event_key = request.query_params.get('event_key')
        if event_key:
            qs = qs.filter(event__event_key=event_key)

        scope = request.query_params.get('scope')
        if scope == 'global':
            qs = qs.filter(website__isnull=True)
        elif scope == 'website':
            qs = qs.filter(website__isnull=False)

        return qs.order_by('event__event_key', 'channel', '-version')

    def get_serializer_class(self):  # type: ignore[override]
        if self.action in ('create', 'update', 'partial_update'):
            return NotificationTemplateCreateSerializer
        return NotificationTemplateSerializer

    def perform_create(self, serializer):
        website = getattr(self.request.user, 'website', None)
        if getattr(self.request.user, 'role', '') == 'superadmin':
            website = serializer.validated_data.get('website', website)
        instance = serializer.save(website=website)
        TemplateService.invalidate_cache(
            event_key=instance.event.event_key,
            channel=instance.channel,
            website=instance.website,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        TemplateService.invalidate_cache(
            event_key=instance.event.event_key,
            channel=instance.channel,
            website=instance.website,
        )

    def perform_destroy(self, instance):
        TemplateService.invalidate_cache(
            event_key=instance.event.event_key,
            channel=instance.channel,
            website=instance.website,
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Render a template with sample context."""
        template = self.get_object()
        context = request.data.get('context', {})
        if not context:
            context = {
                var: f"[{var}]"
                for var in (template.available_variables or [])
            }
        rendered = TemplateService.render(template, context)
        return Response({
            'channel': template.channel,
            'rendered': rendered,
            'context_used': context,
        })

    @action(detail=False, methods=['get'])
    def missing(self, request):
        """List events that have no template for a given channel."""
        from notifications_system.enums import NotificationChannel
        channel = request.query_params.get('channel', NotificationChannel.EMAIL)
        website = getattr(request.user, 'website', None)

        all_events = NotificationEventModel.objects.filter(is_active=True)
        covered_ids = NotificationTemplate.objects.filter(
            channel=channel, is_active=True,
        ).values_list('event_id', flat=True)

        missing = all_events.exclude(id__in=covered_ids)
        return Response({
            'channel': channel,
            'missing_count': missing.count(),
            'missing_events': NotificationEventSerializer(missing, many=True).data,
        })

    @action(detail=False, methods=['get'])
    def coverage(self, request):
        """Template coverage summary per event and channel."""
        from notifications_system.enums import NotificationChannel
        website = getattr(request.user, 'website', None)
        channels = [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
        events = NotificationEventModel.objects.filter(is_active=True)

        coverage = []
        for event in events:
            entry = {
                'event_key': event.event_key,
                'label': event.label,
                'category': event.category,
                'channels': {},
            }
            for channel in channels:
                entry['channels'][channel] = {
                    'global': NotificationTemplate.objects.filter(
                        event=event, channel=channel,
                        website__isnull=True, is_active=True,
                    ).exists(),
                    'website_override': NotificationTemplate.objects.filter(
                        event=event, channel=channel,
                        website=website, is_active=True,
                    ).exists() if website else False,
                }
            coverage.append(entry)
        return Response(coverage)


class NotificationEventConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only event configuration list.
    Used by the frontend preference panel to know which
    events users can configure.
    """
    serializer_class = NotificationEventConfigSerializer

    def get_permissions(self):
        from admin_management.permissions import IsAdmin
        return [IsAdmin()]

    def get_queryset(self) -> QuerySet:  # type: ignore[override]
        from notifications_system.models.event_config import NotificationEventConfig
        return NotificationEventConfig.objects.select_related(
            'event'
        ).filter(is_active=True).order_by('event__category', 'event__event_key')
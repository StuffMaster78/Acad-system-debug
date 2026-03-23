"""
DRF filter backends for notification endpoints.
"""
from __future__ import annotations

from django_filters import rest_framework as filters

from notifications_system.models.notifications import Notification
from notifications_system.enums import (
    NotificationChannel,
    NotificationCategory,
    NotificationPriority,
    DeliveryStatus,
)


class NotificationFilter(filters.FilterSet):
    """
    Filters for the notification feed endpoint.
    All filters are optional and combinable.
    """
    event_key = filters.CharFilter(lookup_expr='icontains')
    category = filters.ChoiceFilter(choices=NotificationCategory.choices)
    priority = filters.ChoiceFilter(choices=NotificationPriority.choices)
    status = filters.ChoiceFilter(choices=DeliveryStatus.choices)
    is_read = filters.BooleanFilter(
        field_name='notificationsuserstatus__is_read',
    )
    is_digest = filters.BooleanFilter()
    is_critical = filters.BooleanFilter()
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
    )

    class Meta:
        model = Notification
        fields = [
            'event_key',
            'category',
            'priority',
            'status',
            'is_read',
            'is_digest',
            'is_critical',
            'created_after',
            'created_before',
        ]
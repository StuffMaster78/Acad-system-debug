from __future__ import annotations

import django_filters

from tickets.models import Ticket


class TicketFilter(django_filters.FilterSet):
    status = django_filters.CharFilter()
    priority = django_filters.CharFilter()
    category = django_filters.CharFilter()
    assigned_to = django_filters.NumberFilter(field_name="assigned_to_id")
    created_by = django_filters.NumberFilter(field_name="created_by_id")
    website = django_filters.NumberFilter(field_name="website_id")
    created_after = django_filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_before = django_filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )
    related_type = django_filters.CharFilter(
        field_name="content_type__model",
    )
    related_id = django_filters.NumberFilter(field_name="object_id")

    class Meta:
        model = Ticket
        fields = [
            "status",
            "priority",
            "category",
            "assigned_to",
            "created_by",
            "website",
            "related_type",
            "related_id",
        ]

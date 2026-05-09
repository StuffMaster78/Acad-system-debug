import django_filters

from writer_payments_management.models.financial_event_models import FinancialEvent
from writer_payments_management.filters.base import BaseFilterSet


class FinancialEventFilter(BaseFilterSet):
    """
    Filters for financial event queries.
    """

    event_type = django_filters.CharFilter(field_name="event_type")
    status = django_filters.CharFilter(field_name="status")

    min_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="gte",
    )
    max_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="lte",
    )

    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = FinancialEvent
        fields = [
            "event_type",
            "status",
        ]
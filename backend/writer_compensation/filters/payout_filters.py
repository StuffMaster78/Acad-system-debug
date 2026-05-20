import django_filters

from writer_compensation.models import PayoutRecord
from writer_compensation.filters.base import BaseFilterSet


class PayoutFilter(BaseFilterSet):
    """
    Filters payout records.
    """

    status = django_filters.CharFilter(field_name="status")
    writer_id = django_filters.NumberFilter(field_name="writer_id")

    min_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="gte",
    )

    max_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="lte",
    )

    class Meta:
        model = PayoutRecord
        fields = ["status", "writer_id"]

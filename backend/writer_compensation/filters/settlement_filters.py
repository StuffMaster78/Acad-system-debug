import django_filters

from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.filters.base import BaseFilterSet


class SettlementFilter(BaseFilterSet):
    """
    Filters settlement periods.
    """

    status = django_filters.CharFilter(field_name="status")
    writer_id = django_filters.NumberFilter(field_name="writer_id")

    min_net = django_filters.NumberFilter(
        field_name="net_payable",
        lookup_expr="gte",
    )
    max_net = django_filters.NumberFilter(
        field_name="net_payable",
        lookup_expr="lte",
    )

    class Meta:
        model = SettlementPeriod
        fields = [
            "status",
            "writer_id",
        ]
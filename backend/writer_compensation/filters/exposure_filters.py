import django_filters

from writer_compensation.models.exposure_ledger_models import ExposureLedger
from writer_compensation.filters.base import BaseFilterSet


class ExposureLedgerFilter(BaseFilterSet):
    """
    Filters exposure ledger queries.
    """

    writer_id = django_filters.NumberFilter(field_name="writer_id")

    min_earned = django_filters.NumberFilter(
        field_name="total_earned",
        lookup_expr="gte",
    )

    max_earned = django_filters.NumberFilter(
        field_name="total_earned",
        lookup_expr="lte",
    )

    class Meta:
        model = ExposureLedger
        fields = ["writer_id"]
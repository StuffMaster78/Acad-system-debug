import django_filters

from writer_payments_management.models.payout_record_models import PayoutRecord
from writer_payments_management.filters.base import BaseFilterSet


class PayoutFilter(BaseFilterSet):
    """
    Filters payout records.
    """

    status = django_filters.CharFilter(field_name="status")
    writer_wallet_id = django_filters.NumberFilter(field_name="writer_wallet_id")

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
        fields = ["status", "writer_wallet_id"]
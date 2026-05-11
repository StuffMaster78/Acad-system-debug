from rest_framework import serializers


class TipSettlementSnapshotSerializer(serializers.Serializer):
    """
    Immutable record of tip settlement outcome.
    """

    tip_id = serializers.IntegerField()

    gross_amount_cents = serializers.IntegerField()
    writer_share_cents = serializers.IntegerField()
    platform_fee_cents = serializers.IntegerField()

    settled_at = serializers.DateTimeField()
    settlement_status = serializers.CharField()
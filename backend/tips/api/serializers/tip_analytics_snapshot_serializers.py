from rest_framework import serializers


class TipAnalyticsSnapshotSerializer(serializers.Serializer):
    """
    Precomputed analytics response.
    """

    total_tips = serializers.IntegerField()
    successful_tips = serializers.IntegerField()
    failed_tips = serializers.IntegerField()
    pending_tips = serializers.IntegerField()

    total_volume_cents = serializers.IntegerField()
    platform_revenue_cents = serializers.IntegerField()
    writer_earnings_cents = serializers.IntegerField()
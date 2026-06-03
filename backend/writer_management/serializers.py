"""
Top-level serializer shim for writer_management.

Some views import directly from `writer_management.serializers`.  Serializers
that belong to the API layer live under `writer_management/api/serializers/`;
this module re-exports the ones referenced from outside that package.
"""

from rest_framework import serializers

from writer_management.models.configs import WriterConfig


class WriterConfigSerializer(serializers.ModelSerializer):
    """Basic read/write serializer for WriterConfig (site-level writer settings)."""

    class Meta:
        model = WriterConfig
        fields = [
            "id",
            "website",
            "takes_enabled",
            "max_requests_per_writer",
            "max_takes_per_writer",
        ]
        read_only_fields = ["id"]


class WriterPaymentViewSerializer(serializers.Serializer):
    """
    Serializer that returns earnings lists for a WriterProfile.

    Returns empty lists until a full earnings aggregation service is wired in.
    The calling view (`views_dashboard.WriterDashboardViewSet.get_payment_info`)
    handles None / empty lists gracefully — totals default to 0.
    """

    order_earnings = serializers.SerializerMethodField()
    special_order_earnings = serializers.SerializerMethodField()
    class_earnings = serializers.SerializerMethodField()

    def get_order_earnings(self, obj):
        return []

    def get_special_order_earnings(self, obj):
        return []

    def get_class_earnings(self, obj):
        return []

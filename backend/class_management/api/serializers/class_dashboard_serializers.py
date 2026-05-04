from __future__ import annotations

from rest_framework import serializers


class ClassDashboardSummarySerializer(serializers.Serializer):
    total_classes = serializers.IntegerField()
    active_classes = serializers.IntegerField()
    completed_classes = serializers.IntegerField()
    cancelled_classes = serializers.IntegerField()
    unpaid_classes = serializers.IntegerField()
    partially_paid_classes = serializers.IntegerField()
    paid_classes = serializers.IntegerField()

    quoted_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    discount_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    final_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    paid_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    balance_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
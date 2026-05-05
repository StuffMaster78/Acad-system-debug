from __future__ import annotations

from rest_framework import serializers


class FixedSpecialOrderPricingPreviewSerializer(serializers.Serializer):
    predefined_config_id = serializers.IntegerField()
    predefined_duration_id = serializers.IntegerField()

    currency = serializers.CharField(
        required=False,
        default="USD",
        max_length=10,
    )

    platform = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=80,
    )

    writer_level = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
    )

    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )
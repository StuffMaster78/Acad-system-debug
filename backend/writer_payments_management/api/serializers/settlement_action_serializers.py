from __future__ import annotations

from rest_framework import serializers


class RunSettlementSerializer(serializers.Serializer):
    website_id = serializers.IntegerField()
    writer_id = serializers.IntegerField()
    payment_window_id = serializers.IntegerField()

    auto_finalize = serializers.BooleanField(
        default=True,
    )
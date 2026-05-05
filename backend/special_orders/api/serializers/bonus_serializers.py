from __future__ import annotations

from rest_framework import serializers


class RequestWriterBonusSerializer(serializers.Serializer):
    writer_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    category = serializers.CharField(max_length=50)
    reason = serializers.CharField()
    metadata = serializers.DictField(required=False)
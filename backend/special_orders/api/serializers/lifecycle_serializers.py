from __future__ import annotations

from rest_framework import serializers


class AssignWriterSerializer(serializers.Serializer):
    writer_id = serializers.IntegerField()
    writer_pay_rule_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    reason = serializers.CharField(required=False, allow_blank=True)


class NotesSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class SubmitWorkSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    mark_ready_for_delivery = serializers.BooleanField(default=False)


class HoldOrderSerializer(serializers.Serializer):
    reason = serializers.CharField()


class ReleaseHoldSerializer(serializers.Serializer):
    restore_status = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True)


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField()


class RequestRevisionSerializer(serializers.Serializer):
    reason = serializers.CharField()
    metadata = serializers.DictField(required=False)


class StartRevisionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
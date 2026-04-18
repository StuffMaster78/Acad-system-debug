from __future__ import annotations

from rest_framework import serializers


class OrderLifecycleSnapshotSerializer(serializers.Serializer):
    """
    Serialize consolidated order lifecycle snapshot data.
    """

    order_id = serializers.IntegerField()
    order_status = serializers.CharField()
    website_id = serializers.IntegerField(allow_null=True)
    client_id = serializers.IntegerField(allow_null=True)

    current_assignment_id = serializers.IntegerField(allow_null=True)
    current_writer_id = serializers.IntegerField(allow_null=True)
    has_current_assignment = serializers.BooleanField()

    active_hold_id = serializers.IntegerField(allow_null=True)
    has_active_hold = serializers.BooleanField()

    pending_reassignment_request_id = serializers.IntegerField(
        allow_null=True
    )
    has_pending_reassignment_request = serializers.BooleanField()

    active_dispute_id = serializers.IntegerField(allow_null=True)
    has_active_dispute = serializers.BooleanField()

    latest_adjustment_request_id = serializers.IntegerField(
        allow_null=True
    )
    latest_adjustment_status = serializers.CharField(allow_null=True)

    latest_revision_request_id = serializers.IntegerField(
        allow_null=True
    )
    latest_revision_status = serializers.CharField(allow_null=True)

    is_revision_window_open = serializers.BooleanField()
    revision_window_days = serializers.IntegerField()
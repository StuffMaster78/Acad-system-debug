from __future__ import annotations

from rest_framework import serializers


class AdjustmentProposalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    proposal_role = serializers.CharField()
    proposal_type = serializers.CharField()
    unit_type = serializers.CharField(allow_null=True)
    currency = serializers.CharField(allow_null=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    scope_payload = serializers.DictField(allow_null=True, default=dict)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class AdjustmentDetailSerializer(serializers.Serializer):
    """
    Full read-only representation of an adjustment request with proposals.
    Returned by GET /orders/{id}/adjustments/latest/ and GET /orders/adjustments/{id}/.
    """

    id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    status = serializers.CharField()
    adjustment_kind = serializers.CharField()
    adjustment_type = serializers.CharField(allow_null=True)
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    unit_type = serializers.CharField(allow_null=True)
    extra_service_code = serializers.CharField(allow_null=True)

    current_quantity = serializers.IntegerField(allow_null=True)
    requested_quantity = serializers.IntegerField(allow_null=True)
    countered_quantity = serializers.IntegerField(allow_null=True)
    quantity_delta = serializers.IntegerField(allow_null=True)

    request_total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    counter_total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    request_writer_compensation_amount = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    counter_writer_compensation_amount = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)

    requested_by_id = serializers.IntegerField(allow_null=True)
    reviewed_by_id = serializers.IntegerField(allow_null=True)

    proposals = AdjustmentProposalSerializer(many=True)

    is_counter_final = serializers.BooleanField()
    escalated_after_counter = serializers.BooleanField()

    expires_at = serializers.DateTimeField(allow_null=True)
    accepted_at = serializers.DateTimeField(allow_null=True)
    declined_at = serializers.DateTimeField(allow_null=True)
    funded_at = serializers.DateTimeField(allow_null=True)
    applied_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

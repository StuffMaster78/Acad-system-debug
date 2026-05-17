from __future__ import annotations

from rest_framework import serializers

from superadmin_management.approvals.models import Approval, ApprovalStep


class ApprovalStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalStep
        fields = [
            "id",
            "approval_id",
            "step_order",
            "approver_role",
            "approver_id",
            "status",
            "acted_at",
        ]


class ApprovalSerializer(serializers.ModelSerializer):
    steps = serializers.SerializerMethodField()

    class Meta:
        model = Approval
        fields = [
            "id",
            "command_id",
            "tenant_id",
            "requested_by",
            "status",
            "current_stage",
            "total_stages",
            "expires_at",
            "escalation_level",
            "metadata",
            "created_at",
            "steps",
        ]

    def get_steps(self, obj):
        steps = ApprovalStep.objects.filter(approval_id=obj.id).order_by("step_order")
        return ApprovalStepSerializer(steps, many=True).data
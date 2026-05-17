from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from superadmin_management.approvals.models import Approval, ApprovalStep
from superadmin_management.approvals.workflows import ApprovalWorkflowEngine
from superadmin_management.api.serializers.approvals import ApprovalSerializer


class ApprovalViewSet(viewsets.ViewSet):

    def list(self, request):
        approvals = Approval.objects.filter(status="pending").order_by("-created_at")
        return Response(ApprovalSerializer(approvals, many=True).data)

    def retrieve(self, request, pk=None):
        approval = Approval.objects.get(id=pk)
        return Response(ApprovalSerializer(approval).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        step = ApprovalStep.objects.filter(
            approval_id=pk,
            status="pending"
        ).order_by("step_order").first()

        result = ApprovalWorkflowEngine.approve_step(step, request.user)
        return Response({"status": "approved", "result": str(result.id)})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        step = ApprovalStep.objects.filter(
            approval_id=pk,
            status="pending"
        ).order_by("step_order").first()

        result = ApprovalWorkflowEngine.reject_step(step, request.user)
        return Response({"status": "rejected", "result": str(result.id)})
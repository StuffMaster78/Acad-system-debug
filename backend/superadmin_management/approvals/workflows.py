from __future__ import annotations

from django.utils import timezone

from superadmin_management.approvals.models import Approval, ApprovalStep
from governance.interceptors.governance_interceptor import GovernanceInterceptors
from event_system.models.event_outbox import EventOutbox


class ApprovalWorkflowEngine:
    """
    Executes multi-stage approval DAGs.
    """

    @staticmethod
    def create(command, tenant, actor, total_stages: int = 1) -> Approval:

        approval = Approval.objects.create(
            command_id=command.id,
            tenant_id=tenant.id,
            requested_by=actor.id,
            total_stages=total_stages,
            current_stage=1,
            status=Approval.Status.PENDING,
        )

        for i in range(total_stages):
            ApprovalStep.objects.create(
                approval_id=approval.id,
                step_order=i + 1,
                approver_role="admin" if i == 0 else "superadmin",
                status=ApprovalStep.Status.PENDING,
            )

        return approval

    @staticmethod
    def approve_step(step: ApprovalStep, actor) -> Approval:

        step.status = ApprovalStep.Status.APPROVED
        step.acted_at = timezone.now()
        step.approver_id = actor.id
        step.save()

        approval = Approval.objects.get(id=step.approval_id)

        approval.current_stage += 1
        approval.save(update_fields=["current_stage"])

        # check if workflow is complete
        if ApprovalWorkflowEngine._is_complete(approval):

            approval.status = Approval.Status.APPROVED
            approval.save(update_fields=["status"])

            return ApprovalWorkflowEngine._finalize(approval)

        return approval

    @staticmethod
    def reject_step(step: ApprovalStep, actor) -> Approval:

        step.status = ApprovalStep.Status.REJECTED
        step.acted_at = timezone.now()
        step.approver_id = actor.id
        step.save()

        approval = Approval.objects.get(id=step.approval_id)

        approval.status = Approval.Status.REJECTED
        approval.save(update_fields=["status"])

        return approval

    @staticmethod
    def _is_complete(approval: Approval) -> bool:
        return approval.current_stage > approval.total_stages

    @staticmethod
    def _finalize(approval: Approval):

        from superadmin_management.commands.models import Command

        command = Command.objects.get(id=approval.command_id)

        # convert command → event (execution boundary)
        event = EventOutbox.objects.create(
            event_type=command.command_type,
            payload=command.payload,
            tenant_id=command.tenant_id,
            actor_id=command.actor_id,
        )

        GovernanceInterceptors.on_command_approved(
            actor=command.actor,
            command=command,
            actor_id=command.actor_id,
            tenant_id=command.tenant_id,
            tenant=tenant,
        )

        return {
            "status": "executed",
            "event_id": event.id,
        }
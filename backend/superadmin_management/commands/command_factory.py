from __future__ import annotations

from governance.contracts.command import Command
from superadmin_management.approvals.models import ApprovalWorkflow


class CommandFactory:

    @staticmethod
    def from_workflow(workflow: ApprovalWorkflow) -> Command:

        return Command(
            command_type=workflow.command_type,
            actor_id=workflow.actor_id,
            tenant_id=workflow.tenant_id,
            payload=workflow.command_payload,
            correlation_id=str(workflow.id),
            idempotency_key=str(workflow.id),
        )
from __future__ import annotations

from celery import shared_task

from superadmin_management.approvals.models import ApprovalWorkflow
from superadmin_management.approvals.services import ApprovalService
from superadmin_management.commands.command_factory import CommandFactory


@shared_task(bind=True, max_retries=5)
def execute_workflow(self, workflow_id: str) -> None:
    """
    Executes workflow AFTER final approval.
    """

    workflow = ApprovalWorkflow.objects.get(id=workflow_id)

    if workflow.status != "approved":
        return

    command = CommandFactory.from_workflow(workflow)

    from governance.command_bus import CommandBus

    CommandBus.dispatch(command)


@shared_task(bind=True)
def expire_workflow(self, workflow_id: str) -> None:
    """
    Auto-expire pending approvals.
    """

    workflow = ApprovalWorkflow.objects.get(id=workflow_id)

    if workflow.status == "pending":
        workflow.status = "expired"
        workflow.save(update_fields=["status"])
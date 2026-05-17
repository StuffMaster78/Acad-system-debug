from celery import shared_task, current_app
from superadmin_management.approvals.models import ApprovalWorkflow
from superadmin_management.approvals.services import ApprovalService
from governance.events.event_bus import GovernanceEventBus
from governance.events.governance_events import GovernanceEvent


@shared_task(
    name="governance.approvals.execute_node",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def execute_node(self, workflow_id: str, node_id: str, actor_id: int | None = None):

    workflow = ApprovalWorkflow.objects.get(id=workflow_id)

    GovernanceEventBus.emit(
        GovernanceEvent(
            event_type="approval.node.started",
            workflow_id=workflow_id,
            node_id=node_id,
            actor_id=actor_id,
            tenant_id=workflow.tenant_id,
            payload={},
        )
    )

    result = ApprovalService.process_node(
        workflow=workflow,
        node_id=node_id,
    )

    event_type = (
        "approval.node.rejected"
        if result.status == "rejected"
        else "approval.node.approved"
    )

    GovernanceEventBus.emit(
        GovernanceEvent(
            event_type=event_type,
            workflow_id=workflow_id,
            node_id=node_id,
            actor_id=actor_id,
            tenant_id=workflow.tenant_id,
            payload={},
        )
    )


@shared_task(name="governance.approvals.trigger_next")
def trigger_next(workflow_id: str, next_node_id: str, actor_id: int | None = None):

    current_app.send_task(
        "governance.approvals.execute_node",
        kwargs={
            "workflow_id": workflow_id,
            "node_id": next_node_id,
            "actor_id": actor_id,
        },
    )
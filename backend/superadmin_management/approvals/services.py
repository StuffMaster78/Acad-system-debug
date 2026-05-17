from __future__ import annotations

import logging
from django.db import transaction

from superadmin_management.approvals.models import (
    ApprovalWorkflow,
    ApprovalNodeState,
    ApprovalAction,
)

from governance.approvals.dag.core.engine import ApprovalDAGEngine
from governance.approvals.dag.core.graph import ApprovalGraph
from governance.approvals.dag.core.state import DAGState
from governance.approvals.dag.persistence.adapter import ApprovalDAGStateAdapter
from governance.approvals.dag.execution.tasks import execute_node

logger = logging.getLogger(__name__)


class ApprovalService:
    """
    Persistence bridge ONLY.

    Responsibilities:
    - Persist workflow state
    - Translate DB ↔ DAG state
    - NO orchestration
    """

    # -----------------------------------
    # CREATE WORKFLOW
    # -----------------------------------
    @staticmethod
    def create_workflow(
        *,
        command_type: str,
        payload: dict,
        actor_id: int,
        tenant_id: int,
        graph: ApprovalGraph,
    ) -> ApprovalWorkflow:

        workflow = ApprovalWorkflow.objects.create(
            command_type=command_type,
            command_payload=payload,
            actor_id=actor_id,
            tenant_id=tenant_id,
            current_node=graph.start_node,
            status="pending",
        )

        ApprovalNodeState.objects.bulk_create([
            ApprovalNodeState(
                workflow=workflow,
                node_id=node_id,
                status="pending",
            )
            for node_id in graph.nodes.keys()
        ])

        return workflow

    # -----------------------------------
    # APPLY ACTION (ADMIN / HUMAN INPUT)
    # -----------------------------------
    @staticmethod
    def apply_action(
        *,
        workflow: ApprovalWorkflow,
        node_id: str,
        actor_id: int,
        action: str,
        graph: ApprovalGraph,
    ) -> ApprovalWorkflow:

        with transaction.atomic():

            node_state = ApprovalNodeState.objects.select_for_update().get(
                workflow=workflow,
                node_id=node_id,
            )

            ApprovalAction.objects.create(
                workflow=workflow,
                node_id=node_id,
                actor_id=actor_id,
                action=action,
            )

            state = ApprovalDAGStateAdapter.to_state(workflow)

            if action == "approve":
                new_state = ApprovalDAGEngine.approve(
                    graph=graph,
                    state=state,
                    node_id=node_id,
                    actor_id=actor_id,
                )
            else:
                new_state = ApprovalDAGEngine.reject(
                    graph=graph,
                    state=state,
                    node_id=node_id,
                    actor_id=actor_id,
                )

            workflow.current_node = new_state.current_node
            workflow.status = (
                "rejected"
                if new_state.is_rejected
                else "approved"
                if new_state.is_complete
                else "pending"
            )
            workflow.save(update_fields=["current_node", "status"])

            node_state.status = (
                "completed" if action == "approve" else "rejected"
            )
            node_state.save(update_fields=["status"])

            return workflow

    # -----------------------------------
    # NODE EXECUTION (SYSTEM FLOW)
    # -----------------------------------
    @staticmethod
    def process_node(
        *,
        workflow: ApprovalWorkflow,
        node_id: str,
        graph: ApprovalGraph,
    ) -> None:

        with transaction.atomic():

            node_state = ApprovalNodeState.objects.select_for_update().get(
                workflow=workflow,
                node_id=node_id,
            )

            # idempotency guard
            if node_state.status in {"completed", "rejected"}:
                return

            # -----------------------------
            # DOMAIN DECISION PLACEHOLDER
            # -----------------------------
            approved = True

            node_state.status = "completed" if approved else "rejected"
            node_state.save(update_fields=["status"])

            if not approved:
                workflow.status = "rejected"
                workflow.save(update_fields=["status"])
                return

            state = ApprovalDAGStateAdapter.to_state(workflow)

            # IMPORTANT:
            # DO NOT rebuild graph from DB unless persisted snapshot exists
            next_nodes = graph.nodes[node_id].on_approve_next

            if not next_nodes:
                workflow.status = "approved"
                workflow.save(update_fields=["status"])
                return

        # -----------------------------------
        # OUTSIDE TRANSACTION: SAFE CELERY FIRE
        # -----------------------------------
        for next_node in next_nodes:
            execute_node.delay(
                str(workflow.id),
                next_node,
                actor_id=workflow.actor_id,
            )
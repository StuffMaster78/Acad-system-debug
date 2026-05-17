from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from governance.approvals.dag.core.graph import ApprovalGraph
from governance.approvals.dag.core.state import DAGState
from governance.approvals.dag.core.engine import ApprovalDAGEngine

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """
    Immutable result of a node execution step.
    """
    workflow_id: str
    node_id: str
    status: str  # approved | rejected | pending
    next_nodes: list[str]


class ApprovalDAGRunnner:
    """
    Pure orchestration layer.

    Responsibilities:
    - Takes current state + graph
    - Executes a single node transition
    - Returns next nodes to trigger
    - Does NOT touch DB or Celery
    """

    @staticmethod
    def run_node(
        *,
        graph: ApprovalGraph,
        state: DAGState,
        node_id: str,
        actor_id: Optional[int] = None,
    ) -> ExecutionResult:
        """
        Execute a single DAG node transition.
        """

        logger.info(
            "Running DAG node",
            extra={
                "graph_id": graph.graph_id,
                "node_id": node_id,
                "actor_id": actor_id,
            },
        )

        # -----------------------------------
        # VALIDATION
        # -----------------------------------
        if node_id not in state.nodes:
            raise ValueError(f"Node not found in state: {node_id}")

        node_state = state.nodes[node_id]

        if node_state.status in {"approved", "rejected"}:
            logger.warning(
                "Skipping already processed node",
                extra={"node_id": node_id, "status": node_state.status},
            )
            return ExecutionResult(
                workflow_id=graph.graph_id,
                node_id=node_id,
                status=node_state.status,
                next_nodes=[],
            )

        # -----------------------------------
        # ENGINE TRANSITION
        # -----------------------------------
        new_state = ApprovalDAGEngine.approve(
            graph=graph,
            state=state,
            node_id=node_id,
            actor_id=actor_id or 0,
        )

        # -----------------------------------
        # DETERMINE NEXT NODES
        # -----------------------------------
        if new_state.is_rejected:
            return ExecutionResult(
                workflow_id=graph.graph_id,
                node_id=node_id,
                status="rejected",
                next_nodes=[],
            )

        if new_state.is_complete:
            return ExecutionResult(
                workflow_id=graph.graph_id,
                node_id=node_id,
                status="approved",
                next_nodes=[],
            )

        next_nodes = graph.get_node(node_id).on_approve_next

        return ExecutionResult(
            workflow_id=graph.graph_id,
            node_id=node_id,
            status="approved",
            next_nodes=next_nodes,
        )
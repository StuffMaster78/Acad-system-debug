from __future__ import annotations

import uuid

from governance.contracts.command import Command
from governance.decision_engine import DecisionEngine
from governance.execution.executor import CommandExecutor
from governance.execution.idempotency import IdempotencyService

from governance.approvals.dag.core.engine import ApprovalDAGEngine
from governance.approvals.dag.core.graph import ApprovalGraph
from governance.approvals.dag.core.state import DAGState
from governance.context import GovernanceContext


class CommandBus:
    """
    SINGLE ENTRY POINT FOR ALL SYSTEM MUTATIONS.

    Flow:
    Command
      ↓
    Policy + Risk + Decision
      ↓
    Approval DAG (if required)
      ↓
    Execution
      ↓
    Event + Audit
    """

    @staticmethod
    def dispatch(command: Command):
        """
        Main governance entry point.
        """

        # -----------------------------------
        # 1. Idempotency Guard
        # -----------------------------------
        if command.idempotency_key:
            IdempotencyService.check_and_lock(
                command.idempotency_key
            )

        # -----------------------------------
        # 2. Decision Phase
        # -----------------------------------
        decision = DecisionEngine.evaluate(command)

        # -----------------------------------
        # 3. HARD BLOCK
        # -----------------------------------
        if not decision.allowed:
            return {
                "status": "blocked",
                "reason": decision.blocked_reason,
            }

        # -----------------------------------
        # 4. APPROVAL REQUIRED → DAG FLOW
        # -----------------------------------
        if decision.requires_approval:

            graph = CommandBus._build_approval_graph(command)

            state = CommandBus._init_state(graph)

            return {
                "status": "pending_approval",
                "graph_id": graph.graph_id,
                "state": state,
            }

        # -----------------------------------
        # 5. DIRECT EXECUTION PATH
        # -----------------------------------
        ctx = GovernanceContext(
            command=command,
            role=getattr(command, "role", None),
            correlation_id=str(uuid.uuid4()),
        )
        
        result = CommandExecutor.execute(ctx)

        return {
            "status": "executed",
            "result": result,
        }

    # -------------------------------------------------------
    # INTERNAL: Approval DAG construction
    # -------------------------------------------------------
    @staticmethod
    def _build_approval_graph(command: Command) -> ApprovalGraph:
        """
        Converts command → approval graph dynamically.
        """

        from governance.approvals.dag.core.node import ApprovalNode

        if command.command_type == "user.delete":

            return ApprovalGraph(
                graph_id=str(uuid.uuid4()),
                start_node="manager_approval",
                nodes={
                    "manager_approval": ApprovalNode(
                        node_id="manager_approval",
                        name="Manager Approval",
                        approvers=[2, 3],
                        requires_all=False,
                        on_approve_next=["superadmin_approval"],
                        on_reject_next=[],
                    ),
                    "superadmin_approval": ApprovalNode(
                        node_id="superadmin_approval",
                        name="Superadmin Approval",
                        approvers=[1],
                        requires_all=True,
                        on_approve_next=[],
                        on_reject_next=[],
                    ),
                },
            )

        # default simple approval flow
        return ApprovalGraph(
            graph_id=str(uuid.uuid4()),
            start_node="single_approval",
            nodes={
                "single_approval": ApprovalNode(
                    node_id="single_approval",
                    name="Default Approval",
                    approvers=[1],
                    requires_all=True,
                    on_approve_next=[],
                    on_reject_next=[],
                ),
            },
        )

    # -------------------------------------------------------
    # INTERNAL: initial state builder
    # -------------------------------------------------------
    @staticmethod
    def _init_state(graph: ApprovalGraph) -> DAGState:

        from governance.approvals.dag.core.state import NodeState

        return DAGState(
            graph_id=graph.graph_id,
            current_node=graph.start_node,
            nodes={
                node_id: NodeState(node_id=node_id)
                for node_id in graph.nodes.keys()
            },
        )
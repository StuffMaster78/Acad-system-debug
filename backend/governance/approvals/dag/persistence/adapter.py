from superadmin_management.approvals.models import ApprovalWorkflow
from governance.approvals.dag.core.state import DAGState, NodeState


class ApprovalDAGStateAdapter:

    @staticmethod
    def to_state(workflow: ApprovalWorkflow) -> DAGState:

        # IMPORTANT: correct related_name MUST exist
        node_states = workflow.node_states.all()

        return DAGState(
            graph_id=str(workflow.id),
            current_node=workflow.current_node,
            nodes={
                n.node_id: NodeState(
                    node_id=n.node_id,
                    status=n.status,
                )
                for n in node_states
            },
            is_complete=workflow.status == "approved",
            is_rejected=workflow.status == "rejected",
        )
from governance.approvals.dag.core.graph import ApprovalGraph
from governance.approvals.dag.core.state import DAGState


class ApprovalDAGEngine:

    @staticmethod
    def approve(
        *,
        graph: ApprovalGraph,
        state: DAGState,
        node_id: str,
        actor_id: int,
    ) -> DAGState:

        state.nodes[node_id].status = "approved"

        node = graph.get_node(node_id)

        next_nodes = node.on_approve_next

        if not next_nodes:
            state.is_complete = True
            return state

        state.current_node = next_nodes[0]
        return state

    @staticmethod
    def reject(
        *,
        graph: ApprovalGraph,
        state: DAGState,
        node_id: str,
        actor_id: int,
    ) -> DAGState:

        state.nodes[node_id].status = "rejected"
        state.is_rejected = True
        return state
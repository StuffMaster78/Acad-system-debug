from dataclasses import dataclass
from typing import Dict

from governance.approvals.dag.core.node import ApprovalNode


@dataclass(frozen=True)
class ApprovalGraph:
    graph_id: str
    start_node: str
    nodes: Dict[str, ApprovalNode]

    def get_node(self, node_id: str) -> ApprovalNode:
        return self.nodes[node_id]
from dataclasses import dataclass, field


@dataclass
class NodeState:
    node_id: str
    status: str = "pending"


@dataclass
class DAGState:
    graph_id: str
    current_node: str

    nodes: dict[str, NodeState] = field(default_factory=dict)

    is_complete: bool = False
    is_rejected: bool = False
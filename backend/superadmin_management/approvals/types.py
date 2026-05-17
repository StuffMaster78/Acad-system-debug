from typing import Protocol, Iterable
from superadmin_management.approvals.models import ApprovalNodeState


class ApprovalWorkflowProtocol(Protocol):
    node_states: Iterable[ApprovalNodeState]
    current_node: str
    status: str
    id: str
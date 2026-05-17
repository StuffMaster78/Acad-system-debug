from dataclasses import dataclass, field


@dataclass(frozen=True)
class ApprovalNode:
    node_id: str
    name: str
    approvers: list[int]
    requires_all: bool = False

    on_approve_next: list[str] = field(default_factory=list)
    on_reject_next: list[str] = field(default_factory=list)
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CommunicationTargetAccessResult:
    """
    Result for target access checks.
    """

    allowed: bool
    reason: str = ""


@dataclass(frozen=True)
class CommunicationTargetContext:
    """
    Normalized communication context for any domain object.
    """

    website: object
    target: object
    client: object | None
    writer: object | None
    staff_users: list[object]
    status: str
    reference: str
    metadata: dict


class CommunicationDomainAdapter(Protocol):
    """
    Adapter contract for apps embedding communication threads.
    """

    target_type: str

    def get_context(self, *, target) -> CommunicationTargetContext:
        """
        Return normalized target context.
        """
        ...

    def user_can_access_target(
        self,
        *,
        user,
        target,
    ) -> CommunicationTargetAccessResult:
        """
        Return whether user can access the target.
        """
        ...

    def get_default_participants(
        self,
        *,
        target,
        thread_kind: str,
    ) -> list[object]:
        """
        Return users to add by default.
        """
        ...
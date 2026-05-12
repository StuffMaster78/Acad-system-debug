from __future__ import annotations

from communications.integrations.base import CommunicationTargetAccessResult
from communications.integrations.base import CommunicationTargetContext


class OrderCommunicationAdapter:
    """
    Adapter exposing orders to the communications app.
    """

    target_type = "order"

    def get_context(self, *, target) -> CommunicationTargetContext:
        """
        Return normalized order communication context.
        """
        return CommunicationTargetContext(
            website=target.website,
            target=target,
            client=getattr(target, "client", None),
            writer=getattr(target, "writer", None),
            staff_users=[],
            status=str(getattr(target, "status", "")),
            reference=str(getattr(target, "order_number", target.pk)),
            metadata={
                "target_type": self.target_type,
                "order_id": target.pk,
            },
        )

    def user_can_access_target(
        self,
        *,
        user,
        target,
    ) -> CommunicationTargetAccessResult:
        """
        Check order target access.
        """
        if getattr(user, "is_superuser", False):
            return CommunicationTargetAccessResult(True)

        if (
            getattr(user, "is_admin", False)
            or getattr(user, "is_support", False)
        ):
            return CommunicationTargetAccessResult(True)

        if getattr(target, "client_id", None) == user.pk:
            return CommunicationTargetAccessResult(True)

        if getattr(target, "writer_id", None) == user.pk:
            return CommunicationTargetAccessResult(True)

        return CommunicationTargetAccessResult(
            False,
            "User cannot access this order.",
        )

    def get_default_participants(
        self,
        *,
        target,
        thread_kind: str,
    ) -> list[object]:
        """
        Return default participants for order communication.
        """
        participants: list[object] = []

        client = getattr(target, "client", None)
        writer = getattr(target, "writer", None)

        if client is not None:
            participants.append(client)

        if thread_kind in {"client_writer", "writer_support"}:
            if writer is not None:
                participants.append(writer)

        return participants
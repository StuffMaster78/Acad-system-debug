from __future__ import annotations

from communications.integrations.base import (
    CommunicationTargetAccessResult,
    CommunicationTargetContext,
)


class TicketCommunicationAdapter:
    """
    Expose tickets as communication thread targets.
    """

    target_type = "ticket"

    def get_context(self, *, target) -> CommunicationTargetContext:
        participants = [
            user for user in (target.created_by, target.assigned_to) if user
        ]
        return CommunicationTargetContext(
            website=target.website,
            target=target,
            client=target.created_by,
            writer=None,
            staff_users=[target.assigned_to] if target.assigned_to else [],
            status=target.status,
            reference=f"TICKET-{target.id}",
            metadata={
                "ticket_id": target.id,
                "category": target.category,
                "priority": target.priority,
                "participant_ids": [user.id for user in participants],
            },
        )

    def user_can_access_target(
        self,
        *,
        user,
        target,
    ) -> CommunicationTargetAccessResult:
        role = getattr(user, "role", None)
        if role in {"admin", "superadmin", "support", "editor"}:
            return CommunicationTargetAccessResult(True)

        if target.created_by_id == getattr(user, "id", None):
            return CommunicationTargetAccessResult(True)

        if target.assigned_to_id == getattr(user, "id", None):
            return CommunicationTargetAccessResult(True)

        return CommunicationTargetAccessResult(
            False,
            "User is not a ticket participant.",
        )

    def get_default_participants(
        self,
        *,
        target,
        thread_kind: str,
    ) -> list[object]:
        seen = set()
        participants = []
        for user in (target.created_by, target.assigned_to):
            if user and user.id not in seen:
                participants.append(user)
                seen.add(user.id)
        return participants

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from communications.models.audit import CommunicationAuditAction
from communications.models.assignment import CommunicationThreadAssignment
from communications.services.audit_service import CommunicationAuditService


class CommunicationThreadAssignmentService:
    """
    Manage staff ownership of communication threads.
    """

    @staticmethod
    @transaction.atomic
    def assign(
        *,
        thread,
        assigned_to,
        assigned_by=None,
    ) -> CommunicationThreadAssignment:
        """
        Assign a thread to a staff user.
        """
        assignment, created = (
            CommunicationThreadAssignment.objects.update_or_create(
                thread=thread,
                assigned_to=assigned_to,
                is_active=True,
                defaults={
                    "website": thread.website,
                    "assigned_by": assigned_by,
                    "unassigned_at": None,
                },
            )
        )

        CommunicationAuditService.log(
            website=thread.website,
            thread=thread,
            actor=assigned_by,
            action=CommunicationAuditAction.PARTICIPANT_ADDED,
            details={
                "assignment_id": assignment.pk,
                "assigned_to_id": assigned_to.id,
                "created": created,
            },
        )

        return assignment

    @staticmethod
    @transaction.atomic
    def unassign(
        *,
        thread,
        assigned_to,
        actor=None,
    ) -> None:
        """
        Remove active assignment from a user.
        """
        CommunicationThreadAssignment.objects.filter(
            thread=thread,
            assigned_to=assigned_to,
            is_active=True,
        ).update(
            is_active=False,
            unassigned_at=timezone.now(),
        )

        CommunicationAuditService.log(
            website=thread.website,
            thread=thread,
            actor=actor,
            action=CommunicationAuditAction.PARTICIPANT_REMOVED,
            details={"assigned_to_id": assigned_to.id},
        )

    @staticmethod
    @transaction.atomic
    def reassign(
        *,
        thread,
        old_assignee,
        new_assignee,
        actor=None,
    ) -> CommunicationThreadAssignment:
        """
        Move ownership from one staff user to another.
        """
        if old_assignee is not None:
            CommunicationThreadAssignmentService.unassign(
                thread=thread,
                assigned_to=old_assignee,
                actor=actor,
            )

        return CommunicationThreadAssignmentService.assign(
            thread=thread,
            assigned_to=new_assignee,
            assigned_by=actor,
        )
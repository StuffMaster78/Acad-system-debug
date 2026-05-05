from __future__ import annotations

from django.db import transaction

from communications.models.audit import CommunicationAuditAction
from communications.models.tag import (
    CommunicationThreadTag,
    CommunicationThreadTagAssignment,
)
from communications.services.audit_service import CommunicationAuditService


class CommunicationThreadTagService:
    """
    Manage communication thread tags.
    """

    @staticmethod
    def create_tag(
        *,
        website,
        name: str,
        color: str = "",
        description: str = "",
    ) -> CommunicationThreadTag:
        """
        Create or return a tenant scoped tag.
        """
        tag, _ = CommunicationThreadTag.objects.get_or_create(
            website=website,
            name=name,
            defaults={
                "color": color,
                "description": description,
            },
        )
        return tag

    @staticmethod
    @transaction.atomic
    def assign_tag(
        *,
        thread,
        tag,
        actor=None,
    ) -> CommunicationThreadTagAssignment:
        """
        Attach a tag to a thread.
        """
        assignment, created = CommunicationThreadTagAssignment.objects.get_or_create(
            website=thread.website,
            thread=thread,
            tag=tag,
        )

        if created:
            CommunicationAuditService.log(
                website=thread.website,
                thread=thread,
                actor=actor,
                action=CommunicationAuditAction.TAG_ADDED,
                details={"tag_id": tag.id, "tag_name": tag.name},
            )

        return assignment

    @staticmethod
    @transaction.atomic
    def remove_tag(
        *,
        thread,
        tag,
        actor=None,
    ) -> None:
        """
        Remove a tag from a thread.
        """
        CommunicationThreadTagAssignment.objects.filter(
            website=thread.website,
            thread=thread,
            tag=tag,
        ).delete()

        CommunicationAuditService.log(
            website=thread.website,
            thread=thread,
            actor=actor,
            action=CommunicationAuditAction.TAG_REMOVED,
            details={"tag_id": tag.id, "tag_name": tag.name},
        )
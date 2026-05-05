from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationAttachment
from communications.models.attachment import CommunicationAttachment
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)

class CommunicationAttachmentSelector:
    """
    Read helpers for communication attachments.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationAttachment]:
        """
        Return all attachments for a website.
        """
        return CommunicationAttachment.objects.filter(website=website)

    @staticmethod
    def for_thread(*, website, thread) -> QuerySet[CommunicationAttachment]:
        """
        Return attachments for a thread.
        """
        return (
            CommunicationAttachment.objects
            .filter(website=website, thread=thread)
            .select_related("thread", "message", "file", "uploaded_by")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def visible_for_thread(
        *,
        website,
        thread,
    ) -> QuerySet[CommunicationAttachment]:
        """
        Return visible attachments for a thread.
        """
        return (
            CommunicationAttachment.objects
            .filter(
                website=website,
                thread=thread,
                is_visible=True,
            )
            .select_related("thread", "message", "file", "uploaded_by")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def for_message(*, website, message) -> QuerySet[CommunicationAttachment]:
        """
        Return attachments for a message.
        """
        return (
            CommunicationAttachment.objects
            .filter(website=website, message=message)
            .select_related("thread", "message", "file", "uploaded_by")
            .order_by("created_at", "id")
        )

    @staticmethod
    def requiring_moderation(
        *,
        website,
    ) -> QuerySet[CommunicationAttachment]:
        """
        Return attachments that require moderation.
        """
        return (
            CommunicationAttachment.objects
            .filter(
                website=website,
                requires_moderation=True,
                is_visible=True,
            )
            .select_related("thread", "message", "file", "uploaded_by")
            .order_by("created_at", "id")
        )
    
    @staticmethod
    def visible_to_user(*, website, user) -> QuerySet[CommunicationAttachment]:
        """
        Return attachments visible to a user.
        """
        base_qs = CommunicationAttachment.objects.filter(website=website)

        if CommunicationThreadGuardService._has_platform_access(user=user):
            return base_qs

        return (
            base_qs
            .filter(
                is_visible=True,
                thread__participant_records__user=user,
                thread__participant_records__can_view=True,
                thread__participant_records__removed_at__isnull=True,
            )
            .distinct()
        )

    @staticmethod
    def visible_for_message(
        *,
        website,
        user,
        message,
    ) -> QuerySet[CommunicationAttachment]:
        """
        Return visible attachments for one message.
        """
        base_qs = CommunicationAttachment.objects.filter(
            website=website,
            message=message,
        )

        if CommunicationThreadGuardService._has_platform_access(user=user):
            return base_qs

        return (
            base_qs
            .filter(
                is_visible=True,
                thread__participant_records__user=user,
                thread__participant_records__can_view=True,
                thread__participant_records__removed_at__isnull=True,
            )
            .distinct()
        )
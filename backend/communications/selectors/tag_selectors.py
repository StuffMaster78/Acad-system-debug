from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationThreadTag
from communications.models import CommunicationThreadTagAssignment


class CommunicationThreadTagSelector:
    """
    Read helpers for thread tags.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationThreadTag]:
        """
        Return all tags for a website.
        """
        return (
            CommunicationThreadTag.objects
            .filter(website=website)
            .order_by("name", "id")
        )

    @staticmethod
    def active_for_website(*, website) -> QuerySet[CommunicationThreadTag]:
        """
        Return active tags for a website.
        """
        return (
            CommunicationThreadTag.objects
            .filter(website=website, is_active=True)
            .order_by("name", "id")
        )

    @staticmethod
    def get_by_name(
        *,
        website,
        name: str,
    ) -> CommunicationThreadTag | None:
        """
        Return a tag by name.
        """
        return (
            CommunicationThreadTag.objects
            .filter(website=website, name__iexact=name)
            .first()
        )


class CommunicationThreadTagAssignmentSelector:
    """
    Read helpers for thread tag assignments.
    """

    @staticmethod
    def for_thread(
        *,
        website,
        thread,
    ) -> QuerySet[CommunicationThreadTagAssignment]:
        """
        Return tags assigned to a thread.
        """
        return (
            CommunicationThreadTagAssignment.objects
            .filter(website=website, thread=thread)
            .select_related("thread", "tag")
            .order_by("tag__name", "id")
        )

    @staticmethod
    def for_tag(
        *,
        website,
        tag,
    ) -> QuerySet[CommunicationThreadTagAssignment]:
        """
        Return thread assignments for a tag.
        """
        return (
            CommunicationThreadTagAssignment.objects
            .filter(website=website, tag=tag)
            .select_related("thread", "tag")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def thread_has_tag(*, website, thread, tag) -> bool:
        """
        Check whether a thread has a tag.
        """
        return CommunicationThreadTagAssignment.objects.filter(
            website=website,
            thread=thread,
            tag=tag,
        ).exists()
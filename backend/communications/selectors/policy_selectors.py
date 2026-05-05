from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationThreadPolicy


class CommunicationThreadPolicySelector:
    """
    Read helpers for communication thread policies.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationThreadPolicy]:
        """
        Return all policies for a website.
        """
        return (
            CommunicationThreadPolicy.objects
            .filter(website=website)
            .order_by("thread_kind", "id")
        )

    @staticmethod
    def active_for_website(*, website) -> QuerySet[CommunicationThreadPolicy]:
        """
        Return active policies for a website.
        """
        return (
            CommunicationThreadPolicy.objects
            .filter(website=website, is_active=True)
            .order_by("thread_kind", "id")
        )

    @staticmethod
    def get_for_kind(
        *,
        website,
        thread_kind: str,
    ) -> CommunicationThreadPolicy | None:
        """
        Return a policy for a specific thread kind.
        """
        return (
            CommunicationThreadPolicy.objects
            .filter(
                website=website,
                thread_kind=thread_kind,
                is_active=True,
            )
            .first()
        )

    @staticmethod
    def attachment_allowed(*, website, thread_kind: str) -> bool:
        """
        Return whether attachments are allowed for a thread kind.
        """
        policy = CommunicationThreadPolicySelector.get_for_kind(
            website=website,
            thread_kind=thread_kind,
        )

        if policy is None:
            return True

        return policy.allow_attachments
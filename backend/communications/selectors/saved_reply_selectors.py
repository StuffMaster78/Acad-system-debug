from __future__ import annotations

from django.db import models
from django.db.models import QuerySet

from communications.models import CommunicationSavedReply


class CommunicationSavedReplySelector:
    """
    Read helpers for saved replies.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationSavedReply]:
        """
        Return all saved replies for a website.
        """
        return (
            CommunicationSavedReply.objects
            .filter(website=website)
            .select_related("created_by")
            .order_by("title", "id")
        )

    @staticmethod
    def active_for_website(*, website) -> QuerySet[CommunicationSavedReply]:
        """
        Return active saved replies for a website.
        """
        return (
            CommunicationSavedReply.objects
            .filter(website=website, is_active=True)
            .select_related("created_by")
            .order_by("title", "id")
        )

    @staticmethod
    def for_category(
        *,
        website,
        category: str,
    ) -> QuerySet[CommunicationSavedReply]:
        """
        Return active saved replies for a category.
        """
        return (
            CommunicationSavedReply.objects
            .filter(
                website=website,
                category__iexact=category,
                is_active=True,
            )
            .select_related("created_by")
            .order_by("title", "id")
        )

    @staticmethod
    def search(
        *,
        website,
        query: str,
    ) -> QuerySet[CommunicationSavedReply]:
        """
        Search active saved replies by title, body, or category.
        """
        return (
            CommunicationSavedReply.objects
            .filter(website=website, is_active=True)
            .filter(
                models.Q(title__icontains=query)
                | models.Q(body__icontains=query)
                | models.Q(category__icontains=query)
            )
            .select_related("created_by")
            .order_by("title", "id")
        )
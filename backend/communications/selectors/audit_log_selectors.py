from __future__ import annotations

from django.db.models import QuerySet

from communications.models import CommunicationAuditLog


class CommunicationAuditLogSelector:
    """
    Read helpers for communication audit logs.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationAuditLog]:
        """
        Return audit logs for a website.
        """
        return (
            CommunicationAuditLog.objects
            .filter(website=website)
            .select_related("thread", "message", "actor")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def for_thread(*, website, thread) -> QuerySet[CommunicationAuditLog]:
        """
        Return audit logs for a thread.
        """
        return (
            CommunicationAuditLog.objects
            .filter(website=website, thread=thread)
            .select_related("thread", "message", "actor")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def for_message(*, website, message) -> QuerySet[CommunicationAuditLog]:
        """
        Return audit logs for a message.
        """
        return (
            CommunicationAuditLog.objects
            .filter(website=website, message=message)
            .select_related("thread", "message", "actor")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def by_actor(*, website, actor) -> QuerySet[CommunicationAuditLog]:
        """
        Return audit logs created by an actor.
        """
        return (
            CommunicationAuditLog.objects
            .filter(website=website, actor=actor)
            .select_related("thread", "message", "actor")
            .order_by("-created_at", "-id")
        )

    @staticmethod
    def by_action(
        *,
        website,
        action: str,
    ) -> QuerySet[CommunicationAuditLog]:
        """
        Return audit logs for an action.
        """
        return (
            CommunicationAuditLog.objects
            .filter(website=website, action=action)
            .select_related("thread", "message", "actor")
            .order_by("-created_at", "-id")
        )
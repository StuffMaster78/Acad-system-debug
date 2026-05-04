from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import ClassPortalWorkLog


class ClassPortalWorkLogSelector:
    """
    Read helpers for portal work logs.
    """

    @staticmethod
    def for_order(*, class_order) -> QuerySet[ClassPortalWorkLog]:
        return (
            ClassPortalWorkLog.objects.filter(class_order=class_order)
            .select_related("writer", "task", "verified_by")
            .order_by("-occurred_at", "-logged_at")
        )

    @staticmethod
    def visible_to_client(*, class_order) -> QuerySet[ClassPortalWorkLog]:
        return ClassPortalWorkLogSelector.for_order(
            class_order=class_order,
        ).filter(visible_to_client=True)

    @staticmethod
    def for_writer(*, website, writer) -> QuerySet[ClassPortalWorkLog]:
        return (
            ClassPortalWorkLog.objects.filter(
                class_order__website=website,
                writer=writer,
            )
            .select_related("class_order", "task")
            .order_by("-occurred_at", "-logged_at")
        )

    @staticmethod
    def unverified_for_website(*, website) -> QuerySet[ClassPortalWorkLog]:
        return (
            ClassPortalWorkLog.objects.filter(
                class_order__website=website,
                verification_status="unverified",
            )
            .select_related("class_order", "writer", "task")
            .order_by("-logged_at")
        )
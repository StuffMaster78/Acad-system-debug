from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import (
    ClassAccessGrant,
    ClassAccessLog,
    ClassTwoFactorRequest,
)


class ClassAccessSelector:
    """
    Read/query helpers for protected class access.
    """

    @staticmethod
    def active_grants_for_order(
        *,
        class_order,
    ) -> QuerySet[ClassAccessGrant]:
        return (
            ClassAccessGrant.objects.filter(
                class_order=class_order,
                status="active",
            )
            .select_related("user", "granted_by")
            .order_by("-granted_at")
        )

    @staticmethod
    def access_logs_for_order(
        *,
        class_order,
    ) -> QuerySet[ClassAccessLog]:
        return (
            ClassAccessLog.objects.filter(class_order=class_order)
            .select_related("viewed_by")
            .order_by("-viewed_at")
        )

    @staticmethod
    def two_factor_requests_for_order(
        *,
        class_order,
    ) -> QuerySet[ClassTwoFactorRequest]:
        return (
            ClassTwoFactorRequest.objects.filter(class_order=class_order)
            .select_related("requested_by")
            .order_by("-requested_at")
        )

    @staticmethod
    def pending_two_factor_requests(*, website):
        return (
            ClassTwoFactorRequest.objects.filter(
                class_order__website=website,
                status__in=["pending", "sent"],
            )
            .select_related("class_order", "requested_by")
            .order_by("needed_by", "-requested_at")
        )
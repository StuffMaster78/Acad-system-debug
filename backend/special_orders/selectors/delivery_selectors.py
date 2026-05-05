from __future__ import annotations

from django.db.models import QuerySet

from special_orders.models import (
    SpecialOrderCompletionLog,
    SpecialOrderDeliverable,
    SpecialOrderDeliveryCheckpoint,
)


class SpecialOrderDeliverySelector:
    """
    Tenant-safe read layer for delivery checkpoints and deliverables.
    """

    @staticmethod
    def list_checkpoints(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderDeliveryCheckpoint]:
        return (
            SpecialOrderDeliveryCheckpoint.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related(
                "required_milestone",
                "unlocked_by",
            )
            .order_by("created_at")
        )

    @staticmethod
    def get_checkpoint(
        *,
        website,
        checkpoint_id: int,
    ) -> SpecialOrderDeliveryCheckpoint:
        return (
            SpecialOrderDeliveryCheckpoint.objects.select_related(
                "special_order",
                "required_milestone",
                "unlocked_by",
            )
            .get(
                id=checkpoint_id,
                website=website,
            )
        )

    @staticmethod
    def list_deliverables(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderDeliverable]:
        return (
            SpecialOrderDeliverable.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related(
                "uploaded_by",
                "reviewed_by",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def list_completion_logs(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderCompletionLog]:
        return (
            SpecialOrderCompletionLog.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related("completed_by")
            .order_by("-created_at")
        )
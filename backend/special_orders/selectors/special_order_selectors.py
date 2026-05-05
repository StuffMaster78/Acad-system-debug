from __future__ import annotations

from django.db.models import QuerySet

from special_orders.models import SpecialOrder


class SpecialOrderSelector:
    """
    Tenant-safe read layer for special orders.
    """

    @staticmethod
    def get_by_id(*, website, special_order_id: int) -> SpecialOrder:
        return (
            SpecialOrder.objects.select_related(
                "client",
                "writer",
                "predefined_config",
                "predefined_duration",
                "accepted_quote",
                "converted_order",
            )
            .get(
                id=special_order_id,
                website=website,
            )
        )

    @staticmethod
    def list_for_client(*, website, client) -> QuerySet[SpecialOrder]:
        return (
            SpecialOrder.objects.filter(
                website=website,
                client=client,
            )
            .select_related(
                "writer",
                "predefined_config",
                "accepted_quote",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def list_for_writer(*, website, writer) -> QuerySet[SpecialOrder]:
        return (
            SpecialOrder.objects.filter(
                website=website,
                writer=writer,
            )
            .select_related(
                "client",
                "predefined_config",
                "accepted_quote",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def list_for_staff(*, website) -> QuerySet[SpecialOrder]:
        return (
            SpecialOrder.objects.filter(
                website=website,
            )
            .select_related(
                "client",
                "writer",
                "predefined_config",
                "accepted_quote",
            )
            .order_by("-created_at")
        )
from __future__ import annotations

from django.db.models import QuerySet

from class_management.models import ClassOrder


class ClassOrderSelector:
    """
    Read/query helpers for class orders.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[ClassOrder]:
        return (
            ClassOrder.objects.filter(website=website)
            .select_related("client", "assigned_writer", "website")
            .prefetch_related("scope_items", "tasks", "timeline_events")
        )

    @classmethod
    def for_client(cls, *, website, client) -> QuerySet[ClassOrder]:
        return cls.for_website(website=website).filter(client=client)

    @classmethod
    def for_writer(cls, *, website, writer) -> QuerySet[ClassOrder]:
        return cls.for_website(website=website).filter(
            assigned_writer=writer,
        )

    @classmethod
    def get_for_website(
        cls,
        *,
        website,
        class_order_id: int,
    ) -> ClassOrder:
        return cls.for_website(website=website).get(pk=class_order_id)

    @classmethod
    def get_for_client(
        cls,
        *,
        website,
        client,
        class_order_id: int,
    ) -> ClassOrder:
        return cls.for_client(
            website=website,
            client=client,
        ).get(pk=class_order_id)

    @classmethod
    def get_for_writer(
        cls,
        *,
        website,
        writer,
        class_order_id: int,
    ) -> ClassOrder:
        return cls.for_writer(
            website=website,
            writer=writer,
        ).get(pk=class_order_id)

    @classmethod
    def active_for_website(cls, *, website) -> QuerySet[ClassOrder]:
        return cls.for_website(website=website).exclude(
            status__in=["completed", "cancelled", "archived"],
        )

    @classmethod
    def unpaid_for_website(cls, *, website) -> QuerySet[ClassOrder]:
        return cls.for_website(website=website).exclude(
            payment_status="paid",
        )
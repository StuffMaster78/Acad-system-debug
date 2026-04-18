from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from orders.models import Order
from orders.models.orders.order_flag import OrderFlag


class OrderFlaggingService:
    """
    Own order flag evaluation and refresh logic.

    Responsibilities:
        1. Apply or remove operational order flags.
        2. Refresh system generated flags.
        3. Support staff or system created classifications.

    This service should not change core lifecycle statuses.
    """

    FLAG_HVO = "hvo"
    FLAG_UO = "uo"
    FLAG_HOT = "hot"
    FLAG_PO = "po"
    FLAG_RCO = "rco"

    HVO_MIN_AMOUNT = 200
    HVO_MIN_PAGES = 15
    UO_THRESHOLD_HOURS = 12
    HOT_THRESHOLD_HOURS = 6

    @classmethod
    @transaction.atomic
    def refresh_flags(
        cls,
        *,
        order: Order,
    ) -> None:
        """
        Refresh all system derived flags for an order.

        Args:
            order:
                Order whose flags should be refreshed.
        """
        cls._refresh_high_value_flag(order=order)
        cls._refresh_urgency_flags(order=order)
        cls._refresh_preferred_order_flag(order=order)
        cls._refresh_returning_client_flag(order=order)

    @classmethod
    def apply_flag(
        cls,
        *,
        order: Order,
        flag_key: str,
        source: str = "system",
        metadata: dict[str, Any] | None = None,
    ) -> OrderFlag:
        """
        Create or activate an order flag.

        Args:
            order:
                Target order.
            flag_key:
                Machine readable flag key.
            source:
                Source of the flag.
            metadata:
                Optional structured metadata.

        Returns:
            OrderFlag:
                Created or updated flag record.
        """
        flag, _ = OrderFlag.objects.update_or_create(
            order=order,
            flag_key=flag_key,
            defaults={
                "website": order.website,
                "source": source,
                "is_active": True,
                "metadata": metadata or {},
            },
        )
        return flag

    @classmethod
    def remove_flag(
        cls,
        *,
        order: Order,
        flag_key: str,
    ) -> None:
        """
        Deactivate a flag on an order if it exists.

        Args:
            order:
                Target order.
            flag_key:
                Flag to deactivate.
        """
        OrderFlag.objects.filter(
            order=order,
            flag_key=flag_key,
            is_active=True,
        ).update(
            is_active=False,
            updated_at=timezone.now(),
        )

    @classmethod
    def _refresh_high_value_flag(
        cls,
        *,
        order: Order,
    ) -> None:
        """
        Refresh the high value order flag.

        Args:
            order:
                Target order.
        """
        total_price = getattr(order, "total_price", 0) or 0
        pages = getattr(order, "pages", 0) or 0

        if (
            total_price >= cls.HVO_MIN_AMOUNT
            or pages >= cls.HVO_MIN_PAGES
        ):
            cls.apply_flag(
                order=order,
                flag_key=cls.FLAG_HVO,
                metadata={
                    "total_amount": total_price,
                    "pages": pages,
                },
            )
            return

        cls.remove_flag(order=order, flag_key=cls.FLAG_HVO)

    @classmethod
    def _refresh_urgency_flags(
        cls,
        *,
        order: Order,
    ) -> None:
        """
        Refresh urgency related flags.

        Args:
            order:
                Target order.
        """
        writer_deadline = getattr(order, "writer_deadline", None)
        if writer_deadline is None:
            cls.remove_flag(order=order, flag_key=cls.FLAG_UO)
            cls.remove_flag(order=order, flag_key=cls.FLAG_HOT)
            return

        seconds_remaining = int(
            (writer_deadline - timezone.now()).total_seconds()
        )
        hours_remaining = seconds_remaining / 3600

        if hours_remaining <= cls.HOT_THRESHOLD_HOURS:
            cls.apply_flag(
                order=order,
                flag_key=cls.FLAG_HOT,
                metadata={"hours_remaining": hours_remaining},
            )
            cls.remove_flag(order=order, flag_key=cls.FLAG_UO)
            return

        if hours_remaining <= cls.UO_THRESHOLD_HOURS:
            cls.apply_flag(
                order=order,
                flag_key=cls.FLAG_UO,
                metadata={"hours_remaining": hours_remaining},
            )
            cls.remove_flag(order=order, flag_key=cls.FLAG_HOT)
            return

        cls.remove_flag(order=order, flag_key=cls.FLAG_UO)
        cls.remove_flag(order=order, flag_key=cls.FLAG_HOT)

    @classmethod
    def _refresh_preferred_order_flag(
        cls,
        *,
        order: Order,
    ) -> None:
        """
        Refresh preferred order flag.

        Args:
            order:
                Target order.
        """
        preferred_writer = getattr(order, "preferred_writer", None)
        if preferred_writer is not None:
            cls.apply_flag(
                order=order,
                flag_key=cls.FLAG_PO,
                metadata={
                    "preferred_writer_id": getattr(
                        preferred_writer,
                        "pk",
                        None,
                    )
                },
            )
            return

        cls.remove_flag(order=order, flag_key=cls.FLAG_PO)

    @classmethod
    def _refresh_returning_client_flag(
        cls,
        *,
        order: Order,
    ) -> None:
        """
        Refresh returning client snapshot flag.

        Args:
            order:
                Target order.

        Notes:
            This is only an operational mirror. The source truth for
            returning client logic should live in the client or CRM side.
        """
        client = getattr(order, "client", None)
        completed_orders_count = getattr(
            client,
            "completed_orders_count",
            0,
        )

        if completed_orders_count and completed_orders_count > 1:
            cls.apply_flag(
                order=order,
                flag_key=cls.FLAG_RCO,
                metadata={
                    "completed_orders_count": completed_orders_count,
                },
            )
            return

        cls.remove_flag(order=order, flag_key=cls.FLAG_RCO)
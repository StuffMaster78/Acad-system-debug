from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders.order_number_sequence import (
    OrderNumberScope,
    OrderNumberSequence,
)


class OrderNumberService:
    """
    Allocate and manage public-facing order numbers.

    Internal DB ids are never modified; this service only manages the
    OrderNumberSequence counters and stamps public_order_number on orders.

    Usage
    -----
    # Admin creates a sequence for July 2026
    seq = OrderNumberService.create_sequence(
        website=website,
        scope="normal_order",
        period="2026-07",
        seed=85673,
        prefix="GC-",
        padding=5,
        created_by=admin_user,
    )

    # When an order is created
    number = OrderNumberService.allocate(
        website=website,
        scope="normal_order",
    )
    # number → "GC-8567300001"
    """

    @staticmethod
    def create_sequence(
        *,
        website,
        scope: str = OrderNumberScope.NORMAL_ORDER,
        period: str | None = None,
        seed: int,
        prefix: str = "",
        padding: int = 5,
        created_by=None,
    ) -> OrderNumberSequence:
        """
        Create a new order number sequence for a given period.

        Raises ValidationError if a sequence for the same website/scope/period
        already exists or if seed/padding values are invalid.
        """
        if seed <= 0:
            raise ValidationError("seed must be a positive integer.")
        if padding < 1 or padding > 15:
            raise ValidationError("padding must be between 1 and 15.")

        if period is None:
            period = timezone.now().strftime("%Y-%m")

        if OrderNumberSequence.objects.filter(
            website=website,
            scope=scope,
            period=period,
        ).exists():
            raise ValidationError(
                f"A sequence for {scope} / {period} already exists on this website. "
                "Deactivate the existing one before creating a new one."
            )

        return OrderNumberSequence.objects.create(
            website=website,
            scope=scope,
            period=period,
            seed=seed,
            prefix=prefix,
            padding=padding,
            next_number=1,
            is_active=True,
            created_by=created_by,
        )

    @classmethod
    @transaction.atomic
    def allocate(
        cls,
        *,
        website,
        scope: str = OrderNumberScope.NORMAL_ORDER,
        period: str | None = None,
    ) -> str | None:
        """
        Atomically allocate the next public order number.

        Returns the formatted number string (e.g. "GC-8567300001") or
        None if no active sequence exists for this website/scope/period.
        The caller should store the returned value on the order.
        """
        if period is None:
            period = timezone.now().strftime("%Y-%m")

        try:
            seq = OrderNumberSequence.objects.select_for_update().get(
                website=website,
                scope=scope,
                period=period,
                is_active=True,
            )
        except OrderNumberSequence.DoesNotExist:
            return None

        number = seq.format_number(seq.next_number)
        seq.next_number += 1
        seq.save(update_fields=["next_number", "updated_at"])
        return number

    @staticmethod
    def deactivate_sequence(sequence: OrderNumberSequence) -> None:
        """Mark a sequence as inactive so it is skipped during allocation."""
        sequence.is_active = False
        sequence.save(update_fields=["is_active", "updated_at"])

    @staticmethod
    def get_active_sequence(
        *,
        website,
        scope: str = OrderNumberScope.NORMAL_ORDER,
        period: str | None = None,
    ) -> OrderNumberSequence | None:
        """Return the active sequence for a website/scope/period, or None."""
        if period is None:
            period = timezone.now().strftime("%Y-%m")
        return OrderNumberSequence.objects.filter(
            website=website,
            scope=scope,
            period=period,
            is_active=True,
        ).first()

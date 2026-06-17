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
    OrderNumberSequence base offsets and stamps public_order_number on orders.

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

    # When order id=2 is created
    number = OrderNumberService.build_reference_for_id(
        website=website,
        object_id=2,
        scope="normal_order",
    )
    # number → "4918002" when seed=4918000 and prefix=""
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
            is_active=True,
        ).exists():
            raise ValidationError(
                f"An active sequence for {scope} / {period} already exists on this website. "
                "Deactivate it before creating a replacement."
            )

        if OrderNumberSequence.objects.filter(
            scope=scope,
            period=period,
            is_active=True,
        ).exclude(seed=seed, prefix=prefix).exists():
            raise ValidationError(
                f"Another active {scope} / {period} sequence uses a different "
                "base or prefix. Use the same base across websites to avoid "
                "leaking website origin through order numbers."
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
    def build_reference_for_id(
        cls,
        *,
        website,
        object_id: int,
        scope: str = OrderNumberScope.NORMAL_ORDER,
        period: str | None = None,
    ) -> str | None:
        """
        Build the public reference from the configured base and object id.

        This deliberately derives from the internal id after the object is
        saved, without exposing the raw database primary key directly.
        Example: seed=4918000 and object_id=2 produces "4918002".
        """
        if period is None:
            period = timezone.now().strftime("%Y-%m")

        if object_id <= 0:
            raise ValidationError("object_id must be a positive integer.")

        seq = cls.get_active_sequence(
            website=website,
            scope=scope,
            period=period,
        )
        if seq is None:
            return None

        return seq.format_number(object_id)

    @classmethod
    @transaction.atomic
    def stamp_order_number(
        cls,
        *,
        order,
        scope: str = OrderNumberScope.NORMAL_ORDER,
        period: str | None = None,
    ) -> str | None:
        """
        Stamp public_order_number on an already-created order.

        The order primary key is the incrementing component. The configured
        sequence seed is only an offset/base, not an independent counter.
        """
        if getattr(order, "public_order_number", None):
            return order.public_order_number

        public_number = cls.build_reference_for_id(
            website=order.website,
            object_id=order.pk,
            scope=scope,
            period=period,
        )
        if public_number is None:
            return None

        order.public_order_number = public_number
        order.save(update_fields=["public_order_number", "updated_at"])
        return public_number

    @classmethod
    @transaction.atomic
    def stamp_public_number(
        cls,
        *,
        instance,
        scope: str,
        field_name: str = "public_order_number",
        period: str | None = None,
    ) -> str | None:
        """
        Stamp a neutral public number on any persisted work item.

        Used by normal orders, class orders, and special orders. The visible
        value is derived from the configured sequence seed plus the object's
        saved primary key, while the database id itself remains internal.
        """
        current_value = getattr(instance, field_name, None)
        if current_value:
            return current_value

        public_number = cls.build_reference_for_id(
            website=instance.website,
            object_id=instance.pk,
            scope=scope,
            period=period,
        )
        if public_number is None:
            return None

        setattr(instance, field_name, public_number)
        update_fields = [field_name]
        if hasattr(instance, "updated_at"):
            update_fields.append("updated_at")
        instance.save(update_fields=update_fields)
        return public_number

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
        Deprecated compatibility path.

        Public order numbers are now derived from the saved order id via
        stamp_order_number(). This method is kept to avoid breaking older
        callers, but new code should not use it.
        """
        seq = cls.get_active_sequence(
            website=website,
            scope=scope,
            period=period,
        )
        if seq is None:
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

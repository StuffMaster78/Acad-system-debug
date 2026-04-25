from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.exceptions import ValidationError

from orders.models.orders.order import Order
from orders.services.order_flagging_service import (
    OrderFlaggingService,
)


@dataclass(frozen=True)
class WriterOrderFitDecision:
    """
    Represent the outcome of evaluating whether a writer can handle an order.
    """

    can_handle: bool
    required_level: int
    writer_level: int
    reason: str
    is_high_value_order: bool
    is_hot_order: bool


class WriterOrderFitService:
    """
    Own writer and order suitability checks.

    Responsibilities:
        1. Determine the required writer level for an order.
        2. Determine whether a specific writer can handle an order.
        3. Provide a structured decision object for staffing workflows.

    Notes:
        1. The source truth for the writer's level should come from the
           writer domain.
        2. This service owns the order side interpretation of difficulty,
           urgency, and high value constraints.
    """

    BASE_REQUIRED_LEVEL = 1
    HVO_REQUIRED_LEVEL = 3
    HOT_REQUIRED_LEVEL = 2
    LARGE_PAGE_COUNT_REQUIRED_LEVEL = 2
    LARGE_PAGE_COUNT_THRESHOLD = 15

    @classmethod
    def get_fit_decision(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> WriterOrderFitDecision:
        """
        Build a structured writer fit decision for an order.

        Args:
            writer:
                Writer being evaluated.
            order:
                Target order.

        Returns:
            WriterOrderFitDecision:
                Structured suitability decision.
        """
        writer_level = cls._get_writer_level(writer=writer)
        required_level = cls.get_required_level(order=order)
        is_high_value_order = cls._is_high_value_order(order=order)
        is_hot_order = cls._is_hot_order(order=order)

        can_handle = writer_level >= required_level

        if can_handle:
            reason = "writer_level_sufficient"
        else:
            reason = "writer_level_insufficient"

        return WriterOrderFitDecision(
            can_handle=can_handle,
            required_level=required_level,
            writer_level=writer_level,
            reason=reason,
            is_high_value_order=is_high_value_order,
            is_hot_order=is_hot_order,
        )

    @classmethod
    def can_writer_handle_order(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> bool:
        """
        Return whether the writer can handle the order.

        Args:
            writer:
                Writer being evaluated.
            order:
                Target order.

        Returns:
            bool:
                True when the writer level satisfies the requirement.
        """
        return cls.get_fit_decision(
            writer=writer,
            order=order,
        ).can_handle

    @classmethod
    def validate_writer_assignment(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> None:
        """
        Validate that the writer can be assigned to the order.

        Args:
            writer:
                Writer being evaluated.
            order:
                Target order.

        Raises:
            ValidationError:
                Raised when the writer is not eligible for the order.
        """
        decision = cls.get_fit_decision(
            writer=writer,
            order=order,
        )
        if not decision.can_handle:
            raise ValidationError(
                (
                    "Writer level is insufficient for this order. "
                    f"Required level: {decision.required_level}. "
                    f"Writer level: {decision.writer_level}."
                )
            )

    @classmethod
    def get_required_level(
        cls,
        *,
        order: Order,
    ) -> int:
        """
        Determine the required writer level for an order.

        Args:
            order:
                Target order.

        Returns:
            int:
                Minimum writer level required to handle the order.
        """
        required_level = cls.BASE_REQUIRED_LEVEL

        if cls._is_high_value_order(order=order):
            required_level = max(
                required_level,
                cls.HVO_REQUIRED_LEVEL,
            )

        if cls._is_hot_order(order=order):
            required_level = max(
                required_level,
                cls.HOT_REQUIRED_LEVEL,
            )

        pages = getattr(order, "pages", 0) or 0
        if pages >= cls.LARGE_PAGE_COUNT_THRESHOLD:
            required_level = max(
                required_level,
                cls.LARGE_PAGE_COUNT_REQUIRED_LEVEL,
            )

        return required_level

    @classmethod
    def _is_high_value_order(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether the order qualifies as high value.

        Args:
            order:
                Target order.

        Returns:
            bool:
                True when the order is a high value order.
        """
        active_flags = getattr(order, "flags", None)
        if active_flags is not None:
            return active_flags.filter(
                flag_key=OrderFlaggingService.FLAG_HVO,
                is_active=True,
            ).exists()

        total_price = getattr(order, "total_price", 0) or 0
        pages = getattr(order, "pages", 0) or 0
        return (
            total_price >= OrderFlaggingService.HVO_MIN_AMOUNT
            or pages >= OrderFlaggingService.HVO_MIN_PAGES
        )

    @classmethod
    def _is_hot_order(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether the order qualifies as hot.

        Args:
            order:
                Target order.

        Returns:
            bool:
                True when the order is extremely urgent.
        """
        active_flags = getattr(order, "flags", None)
        if active_flags is not None:
            return active_flags.filter(
                flag_key=OrderFlaggingService.FLAG_HOT,
                is_active=True,
            ).exists()

        writer_deadline = getattr(order, "writer_deadline", None)
        if writer_deadline is None:
            return False

        from django.utils import timezone

        seconds_remaining = int(
            (writer_deadline - timezone.now()).total_seconds()
        )
        hours_remaining = seconds_remaining / 3600
        return hours_remaining <= OrderFlaggingService.HOT_THRESHOLD_HOURS

    @staticmethod
    def _get_writer_level(
        *,
        writer: Any,
    ) -> int:
        """
        Extract the writer level from the writer object.

        Args:
            writer:
                Writer being evaluated.

        Returns:
            int:
                Writer level, defaulting to level 1.

        Notes:
            This method is intentionally tolerant because the source truth
            for writer level may currently live in different places while
            the system is being consolidated.
        """
        direct_level = getattr(writer, "level", None)
        if isinstance(direct_level, int):
            return direct_level

        profile = getattr(writer, "writer_profile", None)
        profile_level = getattr(profile, "level", None)
        if isinstance(profile_level, int):
            return profile_level

        return 1
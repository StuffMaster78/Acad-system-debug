from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError

from orders.models import Order, OrderInterest
from orders.models.orders.constants import (
    ORDER_INTEREST_STATUS_PENDING,
    ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_VISIBILITY_POOL,
)


class OrderStaffingPolicy:
    """
    Own staffing validation and eligibility rules.

    This class contains no persistence side effects.
    """

    # -------------------------
    # CORE SHARED VALIDATIONS
    # -------------------------

    @classmethod
    def _ensure_staffing_ready(cls, *, order: Order) -> None:
        if order.status != ORDER_STATUS_READY_FOR_STAFFING:
            raise ValidationError(
                "Only staffing ready orders can be processed."
            )

    @classmethod
    def _ensure_no_current_assignment(
        cls,
        *,
        has_current_assignment: bool,
    ) -> None:
        if has_current_assignment:
            raise ValidationError(
                "Order already has an active assignment."
            )

    @classmethod
    def _ensure_pool_visible(cls, *, order: Order) -> None:
        if order.visibility_mode != ORDER_VISIBILITY_POOL:
            raise ValidationError(
                "Only pool visible orders allow this operation."
            )

    @classmethod
    def validate_writer_website(
        cls,
        *,
        writer: Any,
        order: Order,
    ) -> None:
        writer_website_id = getattr(writer, "website_id", None)
        if (
            writer_website_id is not None
            and writer_website_id != order.website.pk
        ):
            raise ValidationError(
                "Writer website must match order website."
            )

    # -------------------------
    # ROUTING
    # -------------------------

    @classmethod
    def validate_can_route_order(
        cls,
        *,
        order: Order,
        has_current_assignment: bool,
    ) -> None:
        cls._ensure_staffing_ready(order=order)
        cls._ensure_no_current_assignment(
            has_current_assignment=has_current_assignment
        )

    # -------------------------
    # INTEREST
    # -------------------------

    @classmethod
    def validate_can_express_interest(
        cls,
        *,
        order: Order,
        writer: Any,
        has_current_assignment: bool,
        has_pending_interest: bool,
    ) -> None:
        cls._ensure_staffing_ready(order=order)
        cls._ensure_pool_visible(order=order)
        cls.validate_writer_website(writer=writer, order=order)
        cls._ensure_no_current_assignment(
            has_current_assignment=has_current_assignment
        )

        if has_pending_interest:
            raise ValidationError(
                "Writer already has a pending interest for this order."
            )

    @classmethod
    def validate_can_withdraw_interest(
        cls,
        *,
        interest: OrderInterest,
        writer: Any,
    ) -> None:
        if interest.writer != writer:
            raise ValidationError(
                "Only the writer who created the interest can withdraw it."
            )

        if interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending interest can be withdrawn."
            )

    # -------------------------
    # TAKE / ASSIGN
    # -------------------------

    @classmethod
    def validate_can_take_order(
        cls,
        *,
        order: Order,
        writer: Any,
        has_current_assignment: bool,
    ) -> None:
        cls._ensure_staffing_ready(order=order)
        cls._ensure_pool_visible(order=order)
        cls.validate_writer_website(writer=writer, order=order)
        cls._ensure_no_current_assignment(
            has_current_assignment=has_current_assignment
        )

    @classmethod
    def validate_can_assign_from_interest(
        cls,
        *,
        order: Order,
        interest: OrderInterest,
        has_current_assignment: bool,
    ) -> None:
        cls._ensure_staffing_ready(order=order)
        cls._ensure_no_current_assignment(
            has_current_assignment=has_current_assignment
        )

        if interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending interest can be assigned."
            )

    @classmethod
    def validate_can_assign_directly(
        cls,
        *,
        order: Order,
        writer: Any,
        has_current_assignment: bool,
    ) -> None:
        cls._ensure_staffing_ready(order=order)
        cls.validate_writer_website(writer=writer, order=order)
        cls._ensure_no_current_assignment(
            has_current_assignment=has_current_assignment
        )

    # -------------------------
    # PREFERRED WRITER FLOW
    # -------------------------

    @classmethod
    def validate_can_accept_preferred_invitation(
        cls,
        *,
        order: Order,
        interest: OrderInterest,
        writer: Any,
        has_current_assignment: bool,
    ) -> None:
        cls._ensure_staffing_ready(order=order)
        cls.validate_writer_website(writer=writer, order=order)
        cls._ensure_no_current_assignment(
            has_current_assignment=has_current_assignment
        )

        if interest.writer != writer:
            raise ValidationError(
                "Only the invited writer can accept this invitation."
            )

        if (
            interest.interest_type
            != ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION
        ):
            raise ValidationError(
                "Interest is not a preferred writer invitation."
            )

        if interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending invitations can be accepted."
            )

    @classmethod
    def validate_can_decline_preferred_invitation(
        cls,
        *,
        interest: OrderInterest,
        writer: Any,
    ) -> None:
        if interest.writer != writer:
            raise ValidationError(
                "Only the invited writer can decline this invitation."
            )

        if (
            interest.interest_type
            != ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION
        ):
            raise ValidationError(
                "Interest is not a preferred writer invitation."
            )

        if interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending invitations can be declined."
            )

    @classmethod
    def validate_can_expire_preferred_invitation(
        cls,
        *,
        interest: OrderInterest,
    ) -> None:
        if (
            interest.interest_type
            != ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION
        ):
            raise ValidationError(
                "Interest is not a preferred writer invitation."
            )

        if interest.status != ORDER_INTEREST_STATUS_PENDING:
            raise ValidationError(
                "Only pending invitations can expire."
            )

    # -------------------------
    # RELEASE
    # -------------------------

    @classmethod
    def validate_can_release_to_pool(
        cls,
        *,
        has_current_assignment: bool,
    ) -> None:
        if not has_current_assignment:
            raise ValidationError(
                "Cannot return an order to the pool without an assignment."
            )

    @classmethod
    def validate_no_open_preferred_invitation(
        cls,
        *,
        has_open_invitation: bool,
    ) -> None:
        if has_open_invitation:
            raise ValidationError(
                "Order already has an open preferred writer invitation."
            )
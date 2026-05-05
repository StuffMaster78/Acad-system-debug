from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from special_orders.models import SpecialOrder


class SpecialOrderBonusService:
    """
    Handle writer bonus or earning handoff for special orders.

    This service does not directly mutate wallet balances.
    Wallets and ledger should own actual money movement.
    """

    BONUS_CATEGORIES = {
        "performance",
        "order_completion",
        "client_tip",
        "urgent_delivery",
        "manual_adjustment",
        "other",
    }

    ADMIN_ROLES = {
        "admin",
        "superadmin",
    }

    @classmethod
    @transaction.atomic
    def request_writer_bonus(
        cls,
        *,
        special_order: SpecialOrder,
        writer,
        amount: Decimal,
        category: str,
        reason: str,
        requested_by,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Request a writer bonus for a special order.

        Replace the placeholder return with your actual wallets/ledger
        writer adjustment service call.
        """
        cls._validate_admin(actor=requested_by)
        cls._validate_writer(
            special_order=special_order,
            writer=writer,
        )
        cls._validate_amount(amount=amount)
        cls._validate_category(category=category)

        if not reason.strip():
            raise ValueError("Bonus reason is required.")

        # Recommended future call:
        #
        # adjustment = WriterWalletService.credit_bonus(
        #     website=special_order.website,
        #     writer=writer,
        #     amount=amount,
        #     category=category,
        #     reason=reason,
        #     source_app="special_orders",
        #     source_model="SpecialOrder",
        #     source_object_id=str(special_order.id),
        #     triggered_by=requested_by,
        #     metadata={
        #         "special_order_id": special_order.id,
        #         "category": category,
        #         **(metadata or {}),
        #     },
        # )
        #
        # return adjustment

        return {
            "website_id": special_order.website_id,
            "special_order_id": special_order.id,
            "writer_id": writer.id,
            "amount": amount,
            "category": category,
            "reason": reason.strip(),
            "metadata": metadata or {},
        }

    @classmethod
    def calculate_writer_earning(
        cls,
        *,
        special_order: SpecialOrder,
        order_total: Decimal,
    ) -> Decimal:
        """
        Calculate writer earning from the assigned writer pay rule.

        This only calculates. Actual crediting belongs to wallets/ledger.
        """
        writer_pay_rule = special_order.writer_pay_rule

        if writer_pay_rule is None:
            return Decimal("0.00")

        if writer_pay_rule.fixed_amount is not None:
            return writer_pay_rule.fixed_amount

        if writer_pay_rule.percentage is not None:
            amount = order_total * (
                writer_pay_rule.percentage / Decimal("100.00")
            )
            return amount.quantize(Decimal("0.01"))

        return Decimal("0.00")

    @staticmethod
    def _validate_writer(
        *,
        special_order: SpecialOrder,
        writer,
    ) -> None:
        """
        Validate writer belongs to this order and tenant.
        """
        if getattr(writer, "website_id", None) != special_order.website_id:
            raise ValueError("Writer belongs to another tenant.")

        if str(getattr(writer, "role", "")).lower() != "writer":
            raise ValueError("User must be a writer.")

        if special_order.writer_id != getattr(writer, "id", None):
            raise ValueError("Writer is not assigned to this special order.")

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate bonus amount.
        """
        if amount <= Decimal("0.00"):
            raise ValueError("Bonus amount must be greater than zero.")

    @classmethod
    def _validate_category(cls, *, category: str) -> None:
        """
        Validate bonus category.
        """
        if category not in cls.BONUS_CATEGORIES:
            raise ValueError("Invalid writer bonus category.")

    @classmethod
    def _validate_admin(cls, *, actor) -> None:
        """
        Ensure actor is admin or superadmin.
        """
        role = str(getattr(actor, "role", "")).lower()

        if role not in cls.ADMIN_ROLES:
            raise PermissionError("Writer bonus requires admin access.")
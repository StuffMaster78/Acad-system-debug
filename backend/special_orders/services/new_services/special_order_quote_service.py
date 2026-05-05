from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable

from django.db import transaction
from django.utils import timezone

from special_orders.constants import (
    FundingMilestoneType,
    SpecialOrderPricingMode,
    SpecialOrderQuoteLineType,
    SpecialOrderQuoteStatus,
    SpecialOrderStatus,
)
from special_orders.models import (
    EstimatedSpecialOrderSettings,
    SpecialOrder,
    SpecialOrderPricingSnapshot,
    SpecialOrderQuote,
    SpecialOrderQuoteLine,
)
from special_orders.services.new_services.special_order_funding_plan_service import (
    SpecialOrderFundingPlanService,
)


class SpecialOrderQuoteService:
    """
    Create, update, send, and accept special order quotes.

    Quote acceptance creates an immutable pricing snapshot, then creates
    a funding plan from that snapshot.
    """

    @classmethod
    @transaction.atomic
    def create_quote(
        cls,
        *,
        special_order: SpecialOrder,
        line_items: Iterable[dict[str, Any]],
        created_by=None,
        expires_at=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderQuote:
        """
        Create a draft quote with line items.
        """
        cls._validate_quoted_order(special_order=special_order)

        existing_quote = SpecialOrderQuote.objects.filter(
            website=special_order.website,
            special_order=special_order,
        ).first()
        if existing_quote is not None:
            raise ValueError("Special order already has a quote.")

        normalized_lines = cls._normalize_line_items(line_items=line_items)
        total_amount = cls._calculate_total_amount(
            line_items=normalized_lines,
        )

        quote = SpecialOrderQuote.objects.create(
            website=special_order.website,
            special_order=special_order,
            status=SpecialOrderQuoteStatus.DRAFT,
            currency=special_order.currency,
            total_amount=total_amount,
            discount_amount=cls._calculate_discount_amount(
                line_items=normalized_lines,
            ),
            expires_at=expires_at,
            created_by=created_by,
        )

        cls._create_quote_lines(
            quote=quote,
            line_items=normalized_lines,
        )

        special_order.status = SpecialOrderStatus.QUOTE_PENDING
        special_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return quote

    @classmethod
    @transaction.atomic
    def send_quote(
        cls,
        *,
        quote: SpecialOrderQuote,
        sent_by=None,
    ) -> SpecialOrderQuote:
        """
        Mark a draft quote as sent.
        """
        quote = cls._get_locked_quote(quote=quote)

        if quote.status != SpecialOrderQuoteStatus.DRAFT:
            raise ValueError("Only draft quotes can be sent.")

        quote.status = SpecialOrderQuoteStatus.SENT
        quote.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        special_order = quote.special_order
        special_order.status = SpecialOrderStatus.QUOTE_SENT
        special_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return quote

    @classmethod
    @transaction.atomic
    def accept_quote(
        cls,
        *,
        quote: SpecialOrderQuote,
        accepted_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderPricingSnapshot:
        """
        Accept a quote, freeze pricing, and create funding plan.
        """
        quote = cls._get_locked_quote(quote=quote)

        if quote.status != SpecialOrderQuoteStatus.SENT:
            raise ValueError("Only sent quotes can be accepted.")

        if quote.expires_at and quote.expires_at <= timezone.now():
            quote.status = SpecialOrderQuoteStatus.EXPIRED
            quote.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )
            raise ValueError("Quote has expired.")

        special_order = quote.special_order

        existing_snapshot = SpecialOrderPricingSnapshot.objects.filter(
            website=quote.website,
            special_order=special_order,
        ).first()
        if existing_snapshot is not None:
            return existing_snapshot

        deposit_amount = cls._calculate_deposit_amount(
            special_order=special_order,
            quote=quote,
        )

        snapshot = SpecialOrderPricingSnapshot.objects.create(
            website=quote.website,
            special_order=special_order,
            currency=quote.currency,
            total_amount=quote.total_amount,
            deposit_amount=deposit_amount,
            raw_data=cls._build_snapshot_data(
                quote=quote,
                accepted_by=accepted_by,
                metadata=metadata,
            ),
        )

        quote.status = SpecialOrderQuoteStatus.ACCEPTED
        quote.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        special_order.accepted_quote = quote
        special_order.status = SpecialOrderStatus.QUOTE_ACCEPTED
        special_order.save(
            update_fields=[
                "accepted_quote",
                "status",
                "updated_at",
            ]
        )

        SpecialOrderFundingPlanService.create_from_pricing_snapshot(
            special_order=special_order,
            snapshot=snapshot,
            locked_by=accepted_by,
            metadata={
                "source": "quote_acceptance",
                "quote_id": quote.id,
            },
        )

        return snapshot

    @classmethod
    @transaction.atomic
    def reject_quote(
        cls,
        *,
        quote: SpecialOrderQuote,
        rejected_by=None,
        reason: str = "",
    ) -> SpecialOrderQuote:
        """
        Reject a sent quote.
        """
        quote = cls._get_locked_quote(quote=quote)

        if quote.status not in {
            SpecialOrderQuoteStatus.SENT,
            SpecialOrderQuoteStatus.DRAFT,
        }:
            raise ValueError("Quote cannot be rejected in its current state.")

        quote.status = SpecialOrderQuoteStatus.REJECTED
        quote.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        special_order = quote.special_order
        special_order.status = SpecialOrderStatus.QUOTE_PENDING
        special_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return quote

    @staticmethod
    def _validate_quoted_order(
        *,
        special_order: SpecialOrder,
    ) -> None:
        """
        Ensure order supports custom quoting.
        """
        if special_order.pricing_mode != SpecialOrderPricingMode.QUOTED:
            raise ValueError("Only quoted special orders can receive quotes.")

    @staticmethod
    def _get_locked_quote(
        *,
        quote: SpecialOrderQuote,
    ) -> SpecialOrderQuote:
        """
        Lock quote row for safe state transitions.
        """
        return SpecialOrderQuote.objects.select_for_update().get(
            id=quote.id,
            website=quote.website,
        )

    @classmethod
    def _normalize_line_items(
        cls,
        *,
        line_items: Iterable[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Normalize quote line items and calculate line totals.
        """
        normalized_lines: list[dict[str, Any]] = []

        for item in line_items:
            line_type = str(item["line_type"])
            description = str(item["description"]).strip()
            quantity = int(item.get("quantity", 1))
            unit_price = Decimal(str(item["unit_price"]))

            cls._validate_line_item(
                line_type=line_type,
                description=description,
                quantity=quantity,
                unit_price=unit_price,
            )

            total_price = cls._calculate_line_total(
                line_type=line_type,
                quantity=quantity,
                unit_price=unit_price,
            )

            normalized_lines.append(
                {
                    "line_type": line_type,
                    "description": description,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                }
            )

        if not normalized_lines:
            raise ValueError("At least one quote line is required.")

        return normalized_lines

    @staticmethod
    def _validate_line_item(
        *,
        line_type: str,
        description: str,
        quantity: int,
        unit_price: Decimal,
    ) -> None:
        """
        Validate one quote line item.
        """
        valid_line_types = {
            SpecialOrderQuoteLineType.SERVICE,
            SpecialOrderQuoteLineType.ADDON,
            SpecialOrderQuoteLineType.URGENCY_FEE,
            SpecialOrderQuoteLineType.COMPLEXITY_FEE,
            SpecialOrderQuoteLineType.WRITER_LEVEL_FEE,
            SpecialOrderQuoteLineType.DISCOUNT,
            SpecialOrderQuoteLineType.MANUAL_ADJUSTMENT,
            SpecialOrderQuoteLineType.TAX,
        }

        if line_type not in valid_line_types:
            raise ValueError("Invalid quote line type.")

        if not description:
            raise ValueError("Quote line description is required.")

        if quantity <= 0:
            raise ValueError("Quote line quantity must be greater than zero.")

        if unit_price < Decimal("0.00"):
            raise ValueError("Quote line unit price cannot be negative.")

    @staticmethod
    def _calculate_line_total(
        *,
        line_type: str,
        quantity: int,
        unit_price: Decimal,
    ) -> Decimal:
        """
        Calculate one line total.

        Discount lines are stored as positive values but subtracted from the
        quote total.
        """
        total = unit_price * Decimal(quantity)
        total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if line_type == SpecialOrderQuoteLineType.DISCOUNT:
            return -total

        return total

    @staticmethod
    def _calculate_total_amount(
        *,
        line_items: list[dict[str, Any]],
    ) -> Decimal:
        """
        Calculate quote total from normalized line items.
        """
        total = sum(
            item["total_price"]
            for item in line_items
        )
        total = Decimal(total).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        if total <= Decimal("0.00"):
            raise ValueError("Quote total must be greater than zero.")

        return total

    @staticmethod
    def _calculate_discount_amount(
        *,
        line_items: list[dict[str, Any]],
    ) -> Decimal:
        """
        Return absolute discount amount from discount lines.
        """
        discount_total = sum(
            abs(item["total_price"])
            for item in line_items
            if item["line_type"] == SpecialOrderQuoteLineType.DISCOUNT
        )

        return Decimal(discount_total).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _create_quote_lines(
        *,
        quote: SpecialOrderQuote,
        line_items: list[dict[str, Any]],
    ) -> None:
        """
        Persist quote lines.
        """
        SpecialOrderQuoteLine.objects.bulk_create(
            [
                SpecialOrderQuoteLine(
                    quote=quote,
                    line_type=item["line_type"],
                    description=item["description"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    total_price=item["total_price"],
                )
                for item in line_items
            ]
        )

    @staticmethod
    def _calculate_deposit_amount(
        *,
        special_order: SpecialOrder,
        quote: SpecialOrderQuote,
    ) -> Decimal:
        """
        Calculate deposit amount from tenant settings.
        """
        settings, _created = EstimatedSpecialOrderSettings.objects.get_or_create(
            website=special_order.website,
        )

        percentage_amount = quote.total_amount * (
            settings.default_deposit_percentage / Decimal("100.00")
        )
        deposit_amount = max(
            percentage_amount,
            settings.minimum_deposit_amount,
        )

        deposit_amount = min(deposit_amount, quote.total_amount)

        return deposit_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _build_snapshot_data(
        *,
        quote: SpecialOrderQuote,
        accepted_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build immutable snapshot payload from quote and lines.
        """
        lines = [
            {
                "line_type": line.line_type,
                "description": line.description,
                "quantity": line.quantity,
                "unit_price": str(line.unit_price),
                "total_price": str(line.total_price),
            }
            for line in SpecialOrderQuoteLine.objects.filter(
                quote=quote,
            ).order_by("id")
        ]

        return {
            "quote_id": quote.id,
            "special_order_id": quote.special_order_id,
            "accepted_by_id": getattr(accepted_by, "id", None),
            "accepted_at": timezone.now().isoformat(),
            "currency": quote.currency,
            "total_amount": str(quote.total_amount),
            "discount_amount": str(quote.discount_amount),
            "lines": lines,
            "metadata": metadata or {},
        }
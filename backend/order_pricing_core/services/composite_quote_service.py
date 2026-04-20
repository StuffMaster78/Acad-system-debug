"""
Composite quote service for the order_pricing_core app.
"""

from __future__ import annotations
from dataclasses import dataclass

from decimal import Decimal
from decimal import ROUND_HALF_UP
from typing import cast

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.manager import RelatedManager

from order_pricing_core.models import CompositePricingQuote
from order_pricing_core.models import CompositePricingQuoteItem
from order_pricing_core.models import PricingQuote
from order_pricing_core.models import PricingSnapshot
from order_pricing_core.selectors.composite_quote_selectors import (
    get_composite_quote_by_session_id,
)
from order_pricing_core.validators.composite_quote_validators import (
    validate_component_quotes,
)
from order_pricing_core.validators.composite_quote_validators import (
    validate_composite_not_final,
)
from order_pricing_core.services.snapshot_service import (
    PricingSnapshotService,
)

TWOPLACES = Decimal("0.01")


@dataclass(slots=True)
class CompositeFinalizeResult:
    """
    Typed result returned when a composite quote is finalized.
    """

    composite_quote: CompositePricingQuote
    component_snapshots: list[PricingSnapshot]
    subtotal: Decimal
    discount_amount: Decimal
    total: Decimal
    currency: str


class CompositePricingQuoteService:
    """
    Service for grouping component quotes into one checkout quote.
    """

    @classmethod
    @transaction.atomic
    def create_composite_quote(
        cls,
        *,
        website,
        component_quotes: list[PricingQuote],
        created_by=None,
    ) -> CompositePricingQuote:
        """
        Create a composite quote from component quotes.
        """
        validate_component_quotes(
            website=website,
            quotes=component_quotes,
        )

        currency = cls._get_currency(component_quotes)

        composite_quote = CompositePricingQuote.objects.create(
            website=website,
            currency=currency,
            created_by=created_by,
        )

        cls._replace_items(
            composite_quote=composite_quote,
            component_quotes=component_quotes,
        )
        cls._recalculate_totals(composite_quote=composite_quote)

        return composite_quote

    @classmethod
    @transaction.atomic
    def update_composite_quote(
        cls,
        *,
        composite_quote: CompositePricingQuote,
        component_quotes: list[PricingQuote],
    ) -> CompositePricingQuote:
        """
        Replace component quotes for an existing composite quote.
        """
        validate_composite_not_final(composite_quote.is_final)
        validate_component_quotes(
            website=composite_quote.website,
            quotes=component_quotes,
        )

        cls._replace_items(
            composite_quote=composite_quote,
            component_quotes=component_quotes,
        )
        cls._recalculate_totals(composite_quote=composite_quote)

        return composite_quote

    @classmethod
    @transaction.atomic
    def finalize_composite_quote(
        cls,
        *,
        composite_quote: CompositePricingQuote,
        related_object_type: str = "",
        related_object_id: str = "",
        created_by=None,
    ) -> CompositeFinalizeResult:
        """
        Finalize component quotes into snapshots and lock composite total.
        """
        validate_composite_not_final(composite_quote.is_final)

        items = cls.get_items(composite_quote)
        if not items:
            raise ValidationError(
                {"composite_quote": "Composite quote has no items."}
            )

        component_snapshots: list[PricingSnapshot] = []

        for item in items:
            quote = item.pricing_quote

            if quote.calculated_price is None:
                raise ValidationError(
                    {
                        "component_quotes": (
                            "All component quotes must be calculated "
                            "before finalization."
                        )
                    }
                )

            snapshot = PricingSnapshotService.create_snapshot(
                quote=quote,
                related_object_type=related_object_type,
                related_object_id=related_object_id,
                created_by=created_by,
            )
            component_snapshots.append(snapshot)

        composite_quote.is_final = True
        composite_quote.save(update_fields=["is_final", "updated_at"])

        return CompositeFinalizeResult(
            composite_quote=composite_quote,
            component_snapshots=component_snapshots,
            subtotal=composite_quote.subtotal,
            discount_amount=composite_quote.discount_amount,
            total=composite_quote.total,
            currency=composite_quote.currency,
        )

    @staticmethod
    def get_by_session_id(*, session_id) -> CompositePricingQuote:
        return get_composite_quote_by_session_id(session_id=session_id)

    @staticmethod
    def get_items(
        composite_quote: CompositePricingQuote,
    ) -> list[CompositePricingQuoteItem]:
        items_manager = cast(
            RelatedManager[CompositePricingQuoteItem],
            getattr(composite_quote, "items"),
        )
        return list(items_manager.all().order_by("sort_order", "id"))

    @classmethod
    def _replace_items(
        cls,
        *,
        composite_quote: CompositePricingQuote,
        component_quotes: list[PricingQuote],
    ) -> None:
        items_manager = cast(
            RelatedManager[CompositePricingQuoteItem],
            getattr(composite_quote, "items"),
        )
        items_manager.all().delete()

        item_objects = []

        for index, quote in enumerate(component_quotes, start=1):
            if quote.calculated_price is None:
                raise ValidationError(
                    {
                        "component_quotes": (
                            "Each quote must be calculated before "
                            "being added."
                        )
                    }
                )

            amount = cls._money(quote.calculated_price)

            item_objects.append(
                CompositePricingQuoteItem(
                    composite_quote=composite_quote,
                    pricing_quote=quote,
                    service=quote.service,
                    component_label=quote.service.name,
                    subtotal=amount,
                    total=amount,
                    sort_order=index,
                )
            )

        CompositePricingQuoteItem.objects.bulk_create(item_objects)

    @classmethod
    def _recalculate_totals(
        cls,
        *,
        composite_quote: CompositePricingQuote,
    ) -> None:
        items = cls.get_items(composite_quote)

        subtotal = sum(
            (item.total for item in items),
            start=Decimal("0.00"),
        )
        subtotal = cls._money(subtotal)

        discount_amount = Decimal("0.00")
        total = cls._money(subtotal - discount_amount)

        composite_quote.subtotal = subtotal
        composite_quote.discount_amount = discount_amount
        composite_quote.total = total

        composite_quote.save(
            update_fields=[
                "subtotal",
                "discount_amount",
                "total",
                "updated_at",
            ]
        )

    @staticmethod
    def _get_currency(quotes: list[PricingQuote]) -> str:
        if not quotes:
            raise ValidationError(
                {"component_quotes": "Quotes cannot be empty."}
            )

        first_currency = quotes[0].currency

        for quote in quotes[1:]:
            if quote.currency != first_currency:
                raise ValidationError(
                    {
                        "component_quotes": (
                            "All component quotes must use the same "
                            "currency."
                        )
                    }
                )

        return first_currency

    @staticmethod
    def _money(amount: Decimal) -> Decimal:
        return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    

    @staticmethod
    def build_checkout_payload(
        *,
        composite_quote: CompositePricingQuote,
        component_snapshots: list[PricingSnapshot],
    ) -> dict[str, object]:
        """
        Build a normalized checkout payload for orders app handoff.
        """
        items = CompositePricingQuoteService.get_items(composite_quote)

        return {
            "session_id": str(composite_quote.session_id),
            "currency": composite_quote.currency,
            "subtotal": composite_quote.subtotal,
            "discount_amount": composite_quote.discount_amount,
            "total": composite_quote.total,
            "components": [
                {
                    "service_family": item.service.service_family,
                    "service_code": item.service.service_code,
                    "service_name": item.service.name,
                    "component_label": item.component_label,
                    "pricing_quote_id": item.pricing_quote.id,
                    "subtotal": item.subtotal,
                    "total": item.total,
                    "sort_order": item.sort_order,
                }
                for item in items
            ],
            "component_snapshot_ids": [
                snapshot.pk for snapshot in component_snapshots
            ],
        }
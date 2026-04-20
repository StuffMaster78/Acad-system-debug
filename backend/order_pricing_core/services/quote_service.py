"""
Quote orchestration service for the order_pricing_core app.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from typing import cast

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.manager import RelatedManager

from order_pricing_core.calculators.base import BasePricingCalculator
from order_pricing_core.calculators.base import PriceCalculationResult
from order_pricing_core.calculators.design_order_calculator import (
    DesignOrderPricingCalculator,
)
from order_pricing_core.calculators.diagram_order_calculator import (
    DiagramOrderPricingCalculator,
)
from order_pricing_core.calculators.paper_order_calculator import (
    PaperOrderPricingCalculator,
)
from order_pricing_core.constants import QuoteMode
from order_pricing_core.constants import QuoteStatus
from order_pricing_core.constants import ServiceFamily
from order_pricing_core.models import PricingQuote
from order_pricing_core.models import PricingQuoteInput
from order_pricing_core.models import PricingQuoteLine
from order_pricing_core.models import ServiceCatalogItem
from order_pricing_core.models import WebsitePricingProfile


@dataclass(slots=True)
class QuoteLineResult:
    """
    Typed representation of one quote breakdown line.
    """

    line_type: str
    code: str
    label: str
    amount: Decimal
    metadata: dict[str, Any]


@dataclass(slots=True)
class QuoteOperationResult:
    """
    Typed result returned by quote start/update operations.
    """

    quote: PricingQuote
    lines: list[QuoteLineResult]
    estimated_min_price: Decimal | None
    estimated_max_price: Decimal | None
    calculated_price: Decimal | None
    currency: str
    current_step: int
    status: str


class PricingQuoteService:
    """
    Main service for quote creation, update, and recalculation.
    """

    @classmethod
    @transaction.atomic
    def start_quote(
        cls,
        *,
        website,
        service_code: str,
        payload: dict[str, Any],
        created_by=None,
        mode: str = QuoteMode.ESTIMATE,
    ) -> QuoteOperationResult:
        """
        Create a new quote session and calculate an initial result.
        """
        service = cls._get_service(
            website=website,
            service_code=service_code,
        )
        profile = cls._get_profile(website=website)

        result = cls._get_calculator(
            service_family=service.service_family,
        ).calculate(
            website=website,
            service=service,
            payload=payload,
            mode=mode,
        )

        quote = PricingQuote.objects.create(
            website=website,
            service=service,
            status=cls._status_for_mode(mode=mode),
            current_step=1,
            estimated_min_price=cls._estimated_min(
                result=result,
                mode=mode,
            ),
            estimated_max_price=cls._estimated_max(
                result=result,
                mode=mode,
            ),
            calculated_price=cls._calculated_total(
                result=result,
                mode=mode,
            ),
            currency=profile.currency,
            is_final=(mode == QuoteMode.FINAL),
            created_by=created_by,
        )

        cls._save_quote_input(
            quote=quote,
            service_code=service_code,
            payload=payload,
        )
        cls._replace_quote_lines(quote=quote, result=result)

        return cls._build_operation_result(quote)

    @classmethod
    @transaction.atomic
    def update_quote(
        cls,
        *,
        quote: PricingQuote,
        payload: dict[str, Any],
        step: int | None = None,
        mode: str = QuoteMode.FINAL,
    ) -> QuoteOperationResult:
        """
        Update an existing quote session and recalculate pricing.
        """
        if quote.is_final:
            raise ValidationError(
                {"quote": "Finalized quote cannot be updated."}
            )

        service = quote.service
        website = quote.website
        profile = cls._get_profile(website=website)

        quote_input = cls._get_quote_input(quote)

        merged_payload = cls._merge_payload(
            existing_input=quote_input,
            incoming_payload=payload,
            service_code=service.service_code,
        )

        result = cls._get_calculator(
            service_family=service.service_family,
        ).calculate(
            website=website,
            service=service,
            payload=merged_payload,
            mode=mode,
        )

        quote.status = cls._status_for_mode(mode=mode)
        if step is not None:
            quote.current_step = step
        quote.estimated_min_price = cls._estimated_min(
            result=result,
            mode=mode,
        )
        quote.estimated_max_price = cls._estimated_max(
            result=result,
            mode=mode,
        )
        quote.calculated_price = cls._calculated_total(
            result=result,
            mode=mode,
        )
        quote.currency = profile.currency
        quote.is_final = mode == QuoteMode.FINAL
        quote.save(
            update_fields=[
                "status",
                "current_step",
                "estimated_min_price",
                "estimated_max_price",
                "calculated_price",
                "currency",
                "is_final",
                "updated_at",
            ]
        )

        cls._save_quote_input(
            quote=quote,
            service_code=service.service_code,
            payload=merged_payload,
        )
        cls._replace_quote_lines(quote=quote, result=result)

        return cls._build_operation_result(quote)

    @staticmethod
    def _get_service(
        *,
        website,
        service_code: str,
    ) -> ServiceCatalogItem:
        """
        Return an active service for the website.
        """
        try:
            return ServiceCatalogItem.objects.get(
                website=website,
                service_code=service_code,
                is_active=True,
            )
        except ServiceCatalogItem.DoesNotExist as exc:
            raise ValidationError(
                {"service_code": "Active service not found."}
            ) from exc

    @staticmethod
    def _get_profile(*, website) -> WebsitePricingProfile:
        """
        Return the active pricing profile for the website.
        """
        try:
            return WebsitePricingProfile.objects.get(
                website=website,
                is_active=True,
            )
        except WebsitePricingProfile.DoesNotExist as exc:
            raise ValidationError(
                {"website": "Active pricing profile not found."}
            ) from exc

    @staticmethod
    def _get_calculator(
        *,
        service_family: str,
    ) -> BasePricingCalculator:
        """
        Resolve the correct calculator for a service family.
        """
        if service_family == ServiceFamily.PAPER_ORDER:
            return PaperOrderPricingCalculator()

        if service_family == ServiceFamily.DESIGN_ORDER:
            return DesignOrderPricingCalculator()

        if service_family == ServiceFamily.DIAGRAM_ORDER:
            return DiagramOrderPricingCalculator()

        raise ValidationError(
            {"service_family": "Unsupported service family."}
        )

    @staticmethod
    def _status_for_mode(*, mode: str) -> str:
        """
        Return the correct quote status for a calculation mode.
        """
        if mode == QuoteMode.ESTIMATE:
            return QuoteStatus.ESTIMATED

        if mode == QuoteMode.FINAL:
            return QuoteStatus.CALCULATED

        raise ValidationError({"mode": "Unsupported quote mode."})

    @staticmethod
    def _estimated_min(
        *,
        result: PriceCalculationResult,
        mode: str,
    ) -> Decimal | None:
        """
        Extract estimated minimum price for estimate mode.
        """
        if mode != QuoteMode.ESTIMATE:
            return None

        min_price = result.metadata.get("estimated_min_price")
        if min_price is None:
            return result.total
        return min_price

    @staticmethod
    def _estimated_max(
        *,
        result: PriceCalculationResult,
        mode: str,
    ) -> Decimal | None:
        """
        Extract estimated maximum price for estimate mode.
        """
        if mode != QuoteMode.ESTIMATE:
            return None

        max_price = result.metadata.get("estimated_max_price")
        if max_price is None:
            return result.total
        return max_price

    @staticmethod
    def _calculated_total(
        *,
        result: PriceCalculationResult,
        mode: str,
    ) -> Decimal | None:
        """
        Extract calculated total for final mode.
        """
        if mode == QuoteMode.FINAL:
            return result.total
        return None

    @staticmethod
    def _merge_payload(
        *,
        existing_input: PricingQuoteInput,
        incoming_payload: dict[str, Any],
        service_code: str,
    ) -> dict[str, Any]:
        """
        Merge incoming payload onto persisted input values.
        """
        existing_payload = {
            "service_code": service_code,
            "paper_type_code": existing_input.paper_type_code,
            "work_type_code": existing_input.work_type_code,
            "subject_code": existing_input.subject_code,
            "academic_level_code": existing_input.academic_level_code,
            "analysis_level": existing_input.analysis_level,
            "spacing": existing_input.spacing,
            "pages": existing_input.pages,
            "slides": existing_input.slides,
            "quantity": existing_input.quantity,
            "deadline_hours": existing_input.deadline_hours,
            "diagram_type": existing_input.diagram_type,
            "diagram_complexity": existing_input.diagram_complexity,
            "writer_level_code": existing_input.writer_level_code,
            "preferred_writer_id": existing_input.preferred_writer_id,
            "selected_addon_codes": existing_input.selected_addon_codes,
            "topic": existing_input.topic,
            "instructions": existing_input.instructions,
            "metadata": existing_input.metadata,
        }

        merged = existing_payload.copy()
        merged.update(incoming_payload)
        return merged

    @staticmethod
    def _save_quote_input(
        *,
        quote: PricingQuote,
        service_code: str,
        payload: dict[str, Any],
    ) -> PricingQuoteInput:
        """
        Persist normalized quote input for the session.
        """
        defaults = {
            "service_code": service_code,
            "paper_type_code": payload.get("paper_type_code", ""),
            "work_type_code": payload.get("work_type_code", ""),
            "subject_code": payload.get("subject_code", ""),
            "academic_level_code": payload.get(
                "academic_level_code",
                "",
            ),
            "analysis_level": payload.get("analysis_level", ""),
            "spacing": payload.get("spacing", ""),
            "pages": payload.get("pages"),
            "slides": payload.get("slides"),
            "quantity": payload.get("quantity"),
            "deadline_hours": payload.get("deadline_hours"),
            "diagram_type": payload.get("diagram_type", ""),
            "diagram_complexity": payload.get(
                "diagram_complexity",
                "",
            ),
            "writer_level_code": payload.get(
                "writer_level_code",
                "",
            ),
            "preferred_writer_id": payload.get(
                "preferred_writer_id",
                "",
            ),
            "selected_addon_codes": payload.get(
                "selected_addon_codes",
                [],
            ),
            "topic": payload.get("topic", ""),
            "instructions": payload.get("instructions", ""),
            "metadata": payload.get("metadata", {}),
        }

        quote_input, _ = PricingQuoteInput.objects.update_or_create(
            quote=quote,
            defaults=defaults,
        )
        return quote_input

    @staticmethod
    def _get_quote_input(quote: PricingQuote) -> PricingQuoteInput:
        """
        Return the typed reverse one-to-one quote input relation.
        """
        return cast(
            PricingQuoteInput,
            getattr(quote, "input_data"),
        )

    @staticmethod
    def _get_quote_lines_manager(
        quote: PricingQuote,
    ) -> RelatedManager[PricingQuoteLine]:
        """
        Return the typed reverse manager for quote lines.
        """
        return cast(
            RelatedManager[PricingQuoteLine],
            getattr(quote, "lines"),
        )

    @staticmethod
    def _replace_quote_lines(
        *,
        quote: PricingQuote,
        result: PriceCalculationResult,
    ) -> None:
        """
        Replace persisted quote breakdown lines.
        """
        quote_lines = PricingQuoteService._get_quote_lines_manager(
            quote
        )
        quote_lines.all().delete()

        line_objects = [
            PricingQuoteLine(
                quote=quote,
                line_type=line.line_type,
                code=line.code,
                label=line.label,
                amount=line.amount,
                metadata=line.metadata,
                sort_order=index,
            )
            for index, line in enumerate(result.lines, start=1)
        ]

        PricingQuoteLine.objects.bulk_create(line_objects)

    @staticmethod
    def get_quote_by_session_id(*, session_id) -> PricingQuote:
        """
        Return a quote by session id.
        """
        try:
            return PricingQuote.objects.get(session_id=session_id)
        except PricingQuote.DoesNotExist as exc:
            raise ValidationError(
                {"session_id": "Quote not found."}
            ) from exc

    @staticmethod
    def get_quote_lines(
        quote: PricingQuote,
    ) -> list[PricingQuoteLine]:
        """
        Return ordered quote lines for a quote.
        """
        quote_lines = PricingQuoteService._get_quote_lines_manager(
            quote
        )
        return list(quote_lines.all().order_by("sort_order", "id"))

    @classmethod
    def _build_operation_result(
        cls,
        quote: PricingQuote,
    ) -> QuoteOperationResult:
        """
        Build a typed result for quote operations.
        """
        lines = [
            QuoteLineResult(
                line_type=line.line_type,
                code=line.code,
                label=line.label,
                amount=line.amount,
                metadata=line.metadata,
            )
            for line in cls.get_quote_lines(quote)
        ]

        return QuoteOperationResult(
            quote=quote,
            lines=lines,
            estimated_min_price=quote.estimated_min_price,
            estimated_max_price=quote.estimated_max_price,
            calculated_price=quote.calculated_price,
            currency=quote.currency,
            current_step=quote.current_step,
            status=quote.status,
        )
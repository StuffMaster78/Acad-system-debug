"""
Snapshot service for the order_pricing_core app.
"""

from __future__ import annotations

from typing import cast

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.manager import RelatedManager
from django.utils import timezone

from order_pricing_core.constants import QuoteStatus
from order_pricing_core.models import PricingQuote
from order_pricing_core.models import PricingQuoteInput
from order_pricing_core.models import PricingQuoteLine
from order_pricing_core.models import PricingSnapshot
from order_pricing_core.models import PricingSnapshotLine


class PricingSnapshotService:
    """
    Service for freezing finalized quotes into pricing snapshots.
    """

    @classmethod
    @transaction.atomic
    def create_snapshot(
        cls,
        *,
        quote: PricingQuote,
        related_object_type: str = "",
        related_object_id: str = "",
        created_by=None,
    ) -> PricingSnapshot:
        """
        Create a pricing snapshot from a calculated quote.
        """
        if quote.calculated_price is None:
            raise ValidationError(
                {"quote": "Quote must have a calculated price."}
            )

        quote_input = cls._get_quote_input(quote)
        quote_lines = cls._get_quote_lines_manager(quote)
        ordered_quote_lines = list(
            quote_lines.all().order_by("sort_order", "id")
        )

        snapshot = PricingSnapshot.objects.create(
            website=quote.website,
            service=quote.service,
            quote=quote,
            final_price=quote.calculated_price,
            currency=quote.currency,
            input_data=cls._serialize_quote_input(quote_input),
            breakdown=[
                cls._serialize_quote_line(line)
                for line in ordered_quote_lines
            ],
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            created_by=created_by,
        )

        snapshot_line_objects = [
            PricingSnapshotLine(
                snapshot=snapshot,
                line_type=line.line_type,
                code=line.code,
                label=line.label,
                amount=line.amount,
                metadata=line.metadata,
                sort_order=line.sort_order,
            )
            for line in ordered_quote_lines
        ]
        PricingSnapshotLine.objects.bulk_create(snapshot_line_objects)

        quote.status = QuoteStatus.FINALIZED
        quote.is_final = True
        quote.converted_at = timezone.now()
        quote.converted_object_type = related_object_type
        quote.converted_object_id = related_object_id
        quote.save(
            update_fields=[
                "status",
                "is_final",
                "converted_at",
                "converted_object_type",
                "converted_object_id",
                "updated_at",
            ]
        )

        return snapshot

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
    def _serialize_quote_input(
        quote_input: PricingQuoteInput,
    ) -> dict[str, object]:
        """
        Serialize quote input into snapshot-safe data.
        """
        return {
            "service_code": quote_input.service_code,
            "paper_type_code": quote_input.paper_type_code,
            "work_type_code": quote_input.work_type_code,
            "subject_code": quote_input.subject_code,
            "academic_level_code": quote_input.academic_level_code,
            "analysis_level": quote_input.analysis_level,
            "spacing": quote_input.spacing,
            "pages": quote_input.pages,
            "slides": quote_input.slides,
            "quantity": quote_input.quantity,
            "deadline_hours": quote_input.deadline_hours,
            "diagram_type": quote_input.diagram_type,
            "diagram_complexity": quote_input.diagram_complexity,
            "writer_level_code": quote_input.writer_level_code,
            "preferred_writer_id": quote_input.preferred_writer_id,
            "selected_addon_codes": quote_input.selected_addon_codes,
            "topic": quote_input.topic,
            "instructions": quote_input.instructions,
            "metadata": quote_input.metadata,
        }

    @staticmethod
    def _serialize_quote_line(
        line: PricingQuoteLine,
    ) -> dict[str, object]:
        """
        Serialize a quote line into snapshot-safe data.
        """
        return {
            "line_type": line.line_type,
            "code": line.code,
            "label": line.label,
            "amount": str(line.amount),
            "metadata": line.metadata,
            "sort_order": line.sort_order,
        }
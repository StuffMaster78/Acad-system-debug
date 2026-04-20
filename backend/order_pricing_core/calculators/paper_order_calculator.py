"""
Paper order calculator for the order_pricing_core app.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.core.exceptions import ValidationError

from order_pricing_core.calculators.base import BasePricingCalculator
from order_pricing_core.calculators.base import PriceBreakdownItem
from order_pricing_core.calculators.base import PriceCalculationResult
from order_pricing_core.constants import BreakdownLineType
from order_pricing_core.constants import QuoteMode
from order_pricing_core.constants import SpacingMode
from order_pricing_core.models import AcademicLevelRate
from order_pricing_core.models import AnalysisLevelRate
from order_pricing_core.models import DeadlineRate
from order_pricing_core.models import PaperTypeRate
from order_pricing_core.models import ServiceAddon
from order_pricing_core.models import SubjectRate
from order_pricing_core.models import WorkTypeRate
from order_pricing_core.models import WriterLevelRate
from order_pricing_core.models import WebsitePricingProfile
from order_pricing_core.validators.deadline_validators import (
    deadline_is_tight,
)
from order_pricing_core.validators.deadline_validators import (
    get_recommended_deadline_hours,
)
from order_pricing_core.validators.quote_input_validators import (
    optional_string,
)
from order_pricing_core.validators.quote_input_validators import (
    require_positive_int,
)
from order_pricing_core.validators.quote_input_validators import (
    require_string,
)

TWOPLACES = Decimal("0.01")


class PaperOrderPricingCalculator(BasePricingCalculator):
    """
    Calculator for standard paper-based orders.
    """

    def calculate(
        self,
        *,
        website,
        service,
        payload: dict[str, Any],
        mode: str,
    ) -> PriceCalculationResult:
        """
        Calculate a price result for a paper-based order.
        """
        if mode not in {QuoteMode.ESTIMATE, QuoteMode.FINAL}:
            raise ValidationError({"mode": "Unsupported quote mode."})

        profile = WebsitePricingProfile.objects.get(
            website=website,
            is_active=True,
        )

        pages = require_positive_int(payload, "pages", "Pages")
        deadline_hours = require_positive_int(
            payload,
            "deadline_hours",
            "Deadline hours",
        )
        spacing = payload.get("spacing", SpacingMode.DEFAULT)

        suggestions = self._build_deadline_suggestions(
            profile=profile,
            pages=pages,
            deadline_hours=deadline_hours,
        )

        if mode == QuoteMode.ESTIMATE:
            return self._estimate_result(
                profile=profile,
                pages=pages,
                spacing=spacing,
                suggestions=suggestions,
            )

        return self._final_result(
            website=website,
            profile=profile,
            pages=pages,
            deadline_hours=deadline_hours,
            spacing=require_string(payload, "spacing", "Spacing"),
            paper_type_code=require_string(
                payload,
                "paper_type_code",
                "Paper type",
            ),
            work_type_code=require_string(
                payload,
                "work_type_code",
                "Work type",
            ),
            subject_code=require_string(
                payload,
                "subject_code",
                "Subject",
            ),
            academic_level_code=require_string(
                payload,
                "academic_level_code",
                "Academic level",
            ),
            analysis_level=optional_string(
                payload,
                "analysis_level",
            ),
            writer_level_code=optional_string(
                payload,
                "writer_level_code",
            ),
            preferred_writer_id=optional_string(
                payload,
                "preferred_writer_id",
            ),
            addon_codes=payload.get("selected_addon_codes", []),
            suggestions=suggestions,
        )

    def _estimate_result(
        self,
        *,
        profile: WebsitePricingProfile,
        pages: int,
        spacing: str,
        suggestions: list[dict[str, Any]],
    ) -> PriceCalculationResult:
        """
        Build an estimate-mode result using a min/max range.
        """
        spacing_multiplier = self._get_spacing_multiplier(
            profile=profile,
            spacing=spacing,
        )
        base_amount = self._money(
            Decimal(pages) * profile.base_price_per_page
        )
        base_with_spacing = self._money(base_amount * spacing_multiplier)

        min_multiplier = Decimal("1.0000")
        max_multiplier = Decimal("1.6000")

        min_total = self._money(base_with_spacing * min_multiplier)
        max_total = self._money(base_with_spacing * max_multiplier)

        min_total = self._money(
            max(min_total, profile.minimum_paper_order_charge)
        )
        max_total = self._money(
            max(max_total, profile.minimum_paper_order_charge)
        )

        lines = [
            PriceBreakdownItem(
                line_type=BreakdownLineType.BASE,
                code="estimate_range",
                label="Estimated price range",
                amount=min_total,
                metadata={"max_total": str(max_total)},
            ),
        ]

        return PriceCalculationResult(
            subtotal=min_total,
            discount_amount=Decimal("0.00"),
            total=min_total,
            lines=lines,
            metadata={
                "estimated_min_price": str(min_total),
                "estimated_max_price": str(max_total),
                "pages": pages,
                "spacing": spacing,
            },
            suggestions=suggestions,
        )

    def _final_result(
        self,
        *,
        website,
        profile: WebsitePricingProfile,
        pages: int,
        deadline_hours: int,
        spacing: str,
        paper_type_code: str,
        work_type_code: str,
        subject_code: str,
        academic_level_code: str,
        analysis_level: str,
        writer_level_code: str,
        preferred_writer_id: str,
        addon_codes: list[Any],
        suggestions: list[dict[str, Any]],
    ) -> PriceCalculationResult:
        """
        Build the final calculated price result.
        """
        paper_type_rate = PaperTypeRate.objects.get(
            website=website,
            code=paper_type_code,
            is_active=True,
        )
        work_type_rate = WorkTypeRate.objects.get(
            website=website,
            code=work_type_code,
            is_active=True,
        )
        subject_rate = SubjectRate.objects.select_related(
            "category"
        ).get(
            website=website,
            code=subject_code,
            is_active=True,
        )
        academic_level_rate = AcademicLevelRate.objects.get(
            website=website,
            code=academic_level_code,
            is_active=True,
        )
        deadline_rate = self._get_deadline_rate(
            website=website,
            deadline_hours=deadline_hours,
        )

        lines: list[PriceBreakdownItem] = []

        base_amount = self._money(
            Decimal(pages) * profile.base_price_per_page
        )
        lines.append(
            PriceBreakdownItem(
                line_type=BreakdownLineType.BASE,
                code="base_price",
                label=f"Base price for {pages} pages",
                amount=base_amount,
            )
        )

        subtotal = base_amount

        spacing_multiplier = self._get_spacing_multiplier(
            profile=profile,
            spacing=spacing,
        )
        subtotal = self._apply_multiplier(
            subtotal=subtotal,
            multiplier=spacing_multiplier,
            lines=lines,
            code="spacing",
            label=f"Spacing ({spacing})",
        )

        subtotal = self._apply_multiplier(
            subtotal=subtotal,
            multiplier=paper_type_rate.multiplier,
            lines=lines,
            code="paper_type",
            label=f"Paper type ({paper_type_rate.label})",
        )

        subtotal = self._apply_multiplier(
            subtotal=subtotal,
            multiplier=work_type_rate.multiplier,
            lines=lines,
            code="work_type",
            label=f"Work type ({work_type_rate.label})",
        )

        subtotal = self._apply_multiplier(
            subtotal=subtotal,
            multiplier=academic_level_rate.multiplier,
            lines=lines,
            code="academic_level",
            label=f"Academic level ({academic_level_rate.label})",
        )

        subtotal = self._apply_multiplier(
            subtotal=subtotal,
            multiplier=self._get_subject_multiplier(subject_rate),
            lines=lines,
            code="subject",
            label=f"Subject ({subject_rate.label})",
        )

        subtotal = self._apply_multiplier(
            subtotal=subtotal,
            multiplier=deadline_rate.multiplier,
            lines=lines,
            code="deadline",
            label=f"Deadline ({deadline_rate.label})",
        )

        if analysis_level:
            subtotal = self._apply_analysis_level(
                website=website,
                subtotal=subtotal,
                analysis_level=analysis_level,
                lines=lines,
            )

        if writer_level_code:
            subtotal = self._apply_writer_level(
                website=website,
                subtotal=subtotal,
                writer_level_code=writer_level_code,
                lines=lines,
            )

        if preferred_writer_id:
            subtotal = self._apply_preferred_writer_fee(
                profile=profile,
                subtotal=subtotal,
                lines=lines,
            )

        subtotal = self._apply_addons(
            website=website,
            subtotal=subtotal,
            addon_codes=addon_codes,
            lines=lines,
        )

        subtotal = self._money(
            max(subtotal, profile.minimum_paper_order_charge)
        )

        discount_amount = Decimal("0.00")
        total = self._money(subtotal - discount_amount)

        lines.append(
            PriceBreakdownItem(
                line_type=BreakdownLineType.TOTAL,
                code="total",
                label="Total",
                amount=total,
            )
        )

        return PriceCalculationResult(
            subtotal=subtotal,
            discount_amount=discount_amount,
            total=total,
            lines=lines,
            metadata={
                "pages": pages,
                "deadline_hours": deadline_hours,
                "spacing": spacing,
                "paper_type_code": paper_type_code,
                "work_type_code": work_type_code,
                "subject_code": subject_code,
                "academic_level_code": academic_level_code,
                "analysis_level": analysis_level,
                "writer_level_code": writer_level_code,
                "preferred_writer_id": preferred_writer_id,
                "addon_codes": addon_codes,
            },
            suggestions=suggestions,
        )

    def _get_deadline_rate(
        self,
        *,
        website,
        deadline_hours: int,
    ) -> DeadlineRate:
        """
        Return the first matching deadline band.
        """
        deadline_rate = DeadlineRate.objects.filter(
            website=website,
            is_active=True,
            max_hours__gte=deadline_hours,
        ).order_by("max_hours").first()

        if deadline_rate is None:
            raise ValidationError(
                {"deadline_hours": "No deadline pricing band found."}
            )
        return deadline_rate

    def _get_subject_multiplier(self, subject_rate: SubjectRate) -> Decimal:
        """
        Return the effective subject multiplier.
        """
        if subject_rate.custom_multiplier is not None:
            return subject_rate.custom_multiplier
        return subject_rate.category.multiplier

    def _get_spacing_multiplier(
        self,
        *,
        profile: WebsitePricingProfile,
        spacing: str,
    ) -> Decimal:
        """
        Return the configured spacing multiplier.
        """
        if spacing == SpacingMode.SINGLE:
            return profile.single_spacing_multiplier
        if spacing == SpacingMode.DOUBLE:
            return profile.double_spacing_multiplier
        raise ValidationError({"spacing": "Unsupported spacing mode."})

    def _apply_multiplier(
        self,
        *,
        subtotal: Decimal,
        multiplier: Decimal,
        lines: list[PriceBreakdownItem],
        code: str,
        label: str,
    ) -> Decimal:
        """
        Apply a multiplier and add the delta to breakdown lines.
        """
        new_total = self._money(subtotal * multiplier)
        delta = self._money(new_total - subtotal)

        if delta != Decimal("0.00"):
            lines.append(
                PriceBreakdownItem(
                    line_type=BreakdownLineType.MULTIPLIER,
                    code=code,
                    label=label,
                    amount=delta,
                    metadata={"multiplier": str(multiplier)},
                )
            )

        return new_total

    def _apply_analysis_level(
        self,
        *,
        website,
        subtotal: Decimal,
        analysis_level: str,
        lines: list[PriceBreakdownItem],
    ) -> Decimal:
        """
        Apply analysis-level multiplier when selected.
        """
        analysis_rate = AnalysisLevelRate.objects.get(
            website=website,
            level=analysis_level,
            is_active=True,
        )
        return self._apply_multiplier(
            subtotal=subtotal,
            multiplier=analysis_rate.multiplier,
            lines=lines,
            code="analysis_level",
            label=f"Analysis level ({analysis_level})",
        )

    def _apply_writer_level(
        self,
        *,
        website,
        subtotal: Decimal,
        writer_level_code: str,
        lines: list[PriceBreakdownItem],
    ) -> Decimal:
        """
        Apply writer-level upsell pricing.
        """
        writer_level_rate = WriterLevelRate.objects.get(
            website=website,
            code=writer_level_code,
            is_active=True,
        )

        if writer_level_rate.is_flat_fee:
            fee = self._money(writer_level_rate.amount)
            lines.append(
                PriceBreakdownItem(
                    line_type=BreakdownLineType.FIXED_FEE,
                    code="writer_level",
                    label=f"Writer level ({writer_level_rate.label})",
                    amount=fee,
                )
            )
            return self._money(subtotal + fee)

        return self._apply_multiplier(
            subtotal=subtotal,
            multiplier=writer_level_rate.amount,
            lines=lines,
            code="writer_level",
            label=f"Writer level ({writer_level_rate.label})",
        )

    def _apply_preferred_writer_fee(
        self,
        *,
        profile: WebsitePricingProfile,
        subtotal: Decimal,
        lines: list[PriceBreakdownItem],
    ) -> Decimal:
        """
        Apply preferred-writer flat fee.
        """
        fee = self._money(profile.preferred_writer_fee)
        if fee != Decimal("0.00"):
            lines.append(
                PriceBreakdownItem(
                    line_type=BreakdownLineType.FIXED_FEE,
                    code="preferred_writer",
                    label="Preferred writer fee",
                    amount=fee,
                )
            )
        return self._money(subtotal + fee)

    def _apply_addons(
        self,
        *,
        website,
        subtotal: Decimal,
        addon_codes: list[Any],
        lines: list[PriceBreakdownItem],
    ) -> Decimal:
        """
        Apply selected addon fees.
        """
        if not addon_codes:
            return subtotal

        codes = [
            code for code in addon_codes
            if isinstance(code, str) and code.strip()
        ]
        if not codes:
            return subtotal

        addons = ServiceAddon.objects.filter(
            website=website,
            addon_code__in=codes,
            is_active=True,
        ).order_by("sort_order", "id")

        running_total = subtotal
        for addon in addons:
            fee = self._money(addon.flat_amount)
            lines.append(
                PriceBreakdownItem(
                    line_type=BreakdownLineType.ADDON,
                    code=addon.addon_code,
                    label=addon.name,
                    amount=fee,
                )
            )
            running_total = self._money(running_total + fee)

        return running_total

    def _build_deadline_suggestions(
        self,
        *,
        profile: WebsitePricingProfile,
        pages: int,
        deadline_hours: int,
    ) -> list[dict[str, Any]]:
        """
        Build soft urgency suggestions for tight deadlines.
        """
        suggestions: list[dict[str, Any]] = []

        if not deadline_is_tight(
            pages=pages,
            deadline_hours=deadline_hours,
            max_pages_per_hour=profile.max_pages_per_hour,
        ):
            return suggestions

        recommended_hours = get_recommended_deadline_hours(
            pages=pages,
            max_pages_per_hour=profile.max_pages_per_hour,
            extra_hour_per_extra_page=profile.extra_hour_per_extra_page,
        )

        suggestions.append(
            {
                "type": "deadline_adjustment",
                "message": (
                    "This deadline is tight for the selected page count."
                ),
                "recommended_deadline_hours": recommended_hours,
            }
        )
        suggestions.append(
            {
                "type": "rush_order",
                "message": (
                    "You may proceed as a rush order at a higher urgency "
                    "rate."
                ),
            }
        )

        return suggestions

    def _money(self, amount: Decimal) -> Decimal:
        """
        Normalize money values to two decimal places.
        """
        return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
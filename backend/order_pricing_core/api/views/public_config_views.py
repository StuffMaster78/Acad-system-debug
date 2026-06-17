"""
Public pricing config endpoint for marketing calculators.
"""
from __future__ import annotations

from decimal import Decimal

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from order_configs.models import (
    AcademicLevel,
    EnglishType,
    FormattingandCitationStyle,
    PaperType,
    Subject,
    TypeOfWork,
)
from order_pricing_core.models import (
    AcademicLevelRate,
    DeadlineRate,
    PaperTypeRate,
    ServiceAddon,
    WebsitePricingProfile,
)


def _money(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None


class PublicPricingConfigView(APIView):
    """
    GET /api/v1/pricing/public/config/

    Returns active pricing dimensions AND display option lists for the resolved
    website so marketing calculators stay in sync with backend configuration
    without hardcoding prices or option lists on the frontend.

    Response shape:
        currency                  — ISO code, e.g. "USD"
        base_price_per_page       — website base rate (decimal string or null)
        base_price_per_slide      — slide base rate
        base_price_per_diagram    — diagram base rate
        spacing_multipliers       — { double, single } decimal strings
        academic_levels[]         — code, label, multiplier, price_per_page  (pricing)
        paper_types[]             — code, label, multiplier                   (pricing)
        deadlines[]               — label, max_hours, multiplier              (pricing)
        academic_levels_display[] — name, description                         (display)
        paper_types_display[]     — name, description                         (display)
        subjects[]                — name, category                            (display)
        work_types[]              — name, description                         (display)
        formatting_styles[]       — name                                      (display)
        english_types[]           — name, code                                (display)

    No auth required. Falls back to empty arrays when data is not yet
    configured so the frontend can render its own static fallback values.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request) -> Response:
        website = getattr(request, "website", None)

        if website is None:
            return Response(self._empty())

        profile = WebsitePricingProfile.objects.filter(website=website).first()
        base = profile.base_price_per_page if profile else None

        # ── Pricing dimensions (order_pricing_core) ───────────────────────
        academic_levels = [
            {
                "code": r.code,
                "label": r.label,
                "multiplier": str(r.multiplier),
                "price_per_page": _money(
                    (base * r.multiplier).quantize(Decimal("0.01")) if base else None
                ),
            }
            for r in AcademicLevelRate.objects.filter(website=website, is_active=True)
        ]

        paper_types = [
            {
                "code": r.code,
                "label": r.label,
                "multiplier": str(r.multiplier),
            }
            for r in PaperTypeRate.objects.filter(website=website, is_active=True)
        ]

        deadlines = [
            {
                "label": r.label,
                "max_hours": r.max_hours,
                "multiplier": str(r.multiplier),
            }
            for r in DeadlineRate.objects.filter(website=website, is_active=True)
        ]

        # ── Display option lists (order_configs) ──────────────────────────
        academic_levels_display = [
            {"name": r.name, "description": r.description}
            for r in AcademicLevel.objects.filter(website=website, is_active=True)
        ]

        paper_types_display = [
            {"name": r.name, "description": r.description}
            for r in PaperType.objects.filter(website=website, is_active=True)
        ]

        subjects = [
            {"name": r.name, "category": r.get_category_display()}
            for r in Subject.objects.filter(website=website, is_active=True)
        ]

        work_types = [
            {"name": r.name, "description": r.description}
            for r in TypeOfWork.objects.filter(website=website, is_active=True)
        ]

        formatting_styles = [
            {"name": r.name}
            for r in FormattingandCitationStyle.objects.filter(
                website=website, is_active=True
            )
        ]

        english_types = [
            {"name": r.name, "code": r.code}
            for r in EnglishType.objects.filter(website=website, is_active=True)
        ]

        addons = [
            {
                "id":          a.id,
                "addon_code":  a.addon_code,
                "name":        a.name,
                "description": a.description,
                "flat_amount": str(a.flat_amount),
            }
            for a in ServiceAddon.objects.filter(
                website=website, is_active=True, is_public=True
            ).order_by("sort_order")
        ]

        return Response(
            {
                "currency": profile.currency if profile else "USD",
                "base_price_per_page": _money(base),
                "base_price_per_slide": _money(
                    profile.base_price_per_slide if profile else None
                ),
                "base_price_per_diagram": _money(
                    profile.base_price_per_diagram if profile else None
                ),
                "spacing_multipliers": {
                    "double": str(profile.double_spacing_multiplier) if profile else "1.0000",
                    "single": str(profile.single_spacing_multiplier) if profile else "2.0000",
                },
                "academic_levels": academic_levels,
                "paper_types": paper_types,
                "deadlines": deadlines,
                "academic_levels_display": academic_levels_display,
                "paper_types_display": paper_types_display,
                "subjects": subjects,
                "work_types": work_types,
                "formatting_styles": formatting_styles,
                "english_types": english_types,
                "addons": addons,
            }
        )

    @staticmethod
    def _empty() -> dict:
        return {
            "currency": "USD",
            "base_price_per_page": None,
            "base_price_per_slide": None,
            "base_price_per_diagram": None,
            "spacing_multipliers": {"double": "1.0000", "single": "2.0000"},
            "academic_levels": [],
            "paper_types": [],
            "deadlines": [],
            "academic_levels_display": [],
            "paper_types_display": [],
            "subjects": [],
            "work_types": [],
            "formatting_styles": [],
            "english_types": [],
            "addons": [],
        }

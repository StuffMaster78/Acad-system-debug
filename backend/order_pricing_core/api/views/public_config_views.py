"""
Public pricing config endpoint for marketing calculators.
"""
from __future__ import annotations

from decimal import Decimal

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from order_pricing_core.models import (
    AcademicLevelRate,
    DeadlineRate,
    PaperTypeRate,
    WebsitePricingProfile,
)


def _money(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None


class PublicPricingConfigView(APIView):
    """
    GET /api/v1/pricing/public/config/

    Returns active pricing dimensions for the resolved website so marketing
    calculators stay in sync with backend configuration without hardcoding
    prices or option lists on the frontend.

    Response shape:
        currency                  — ISO code, e.g. "USD"
        base_price_per_page       — website base rate (decimal string or null)
        base_price_per_slide      — slide base rate
        base_price_per_diagram    — diagram base rate
        academic_levels[]         — code, label, multiplier, price_per_page
        paper_types[]             — code, label, multiplier
        deadlines[]               — label, max_hours, multiplier

    No auth required. Falls back to empty arrays when pricing is not yet
    configured so the frontend can render its own static fallback values.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = []

    def get(self, request) -> Response:
        website = getattr(request, "website", None)

        if website is None:
            return Response(self._empty())

        profile = WebsitePricingProfile.objects.filter(website=website).first()
        base = profile.base_price_per_page if profile else None

        academic_levels = [
            {
                "code": r.code,
                "label": r.label,
                "multiplier": str(r.multiplier),
                "price_per_page": _money(
                    (base * r.multiplier).quantize(Decimal("0.01")) if base else None
                ),
            }
            for r in AcademicLevelRate.objects.filter(
                website=website, is_active=True
            )
        ]

        paper_types = [
            {
                "code": r.code,
                "label": r.label,
                "multiplier": str(r.multiplier),
            }
            for r in PaperTypeRate.objects.filter(
                website=website, is_active=True
            )
        ]

        deadlines = [
            {
                "label": r.label,
                "max_hours": r.max_hours,
                "multiplier": str(r.multiplier),
            }
            for r in DeadlineRate.objects.filter(
                website=website, is_active=True
            )
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
                "academic_levels": academic_levels,
                "paper_types": paper_types,
                "deadlines": deadlines,
            }
        )

    @staticmethod
    def _empty() -> dict:
        return {
            "currency": "USD",
            "base_price_per_page": None,
            "base_price_per_slide": None,
            "base_price_per_diagram": None,
            "academic_levels": [],
            "paper_types": [],
            "deadlines": [],
        }

from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from discounts.models.discount_spend_tier import DiscountSpendTier


def _lifetime_spend(user, website) -> Decimal:
    """Compute total completed-payment spend for this client on this website."""
    from payments_processor.models import PaymentIntent
    result = (
        PaymentIntent.objects
        .filter(user=user, website=website, status="completed")
        .aggregate(total=Sum("amount"))["total"]
    )
    return Decimal(str(result)) if result else Decimal("0.00")


class ClientSpendTierProgressView(APIView):
    """
    GET /api/v1/discounts/client/spend-tier-progress/

    Returns all spend tiers for the website with unlock status relative to
    the client's lifetime spend.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        website = getattr(request, "website", None)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)

        lifetime_spend = _lifetime_spend(request.user, website)

        tiers = (
            DiscountSpendTier.objects
            .filter(website=website, is_active=True)
            .select_related("discount")
            .order_by("minimum_lifetime_spend")
        )

        current_tier = None
        next_tier = None
        tier_list = []

        for tier in tiers:
            unlocked = lifetime_spend >= tier.minimum_lifetime_spend
            entry = {
                "id": tier.pk,
                "name": tier.name,
                "minimum_lifetime_spend": str(tier.minimum_lifetime_spend),
                "discount_value": str(tier.discount.discount_value),
                "discount_code": tier.discount.discount_code,
                "discount_type": tier.discount.discount_type,
                "unlocked": unlocked,
            }
            tier_list.append(entry)
            if unlocked:
                current_tier = entry
            elif next_tier is None:
                next_tier = entry

        if next_tier:
            needed = Decimal(next_tier["minimum_lifetime_spend"]) - lifetime_spend
            progress_pct = int(
                (lifetime_spend / Decimal(next_tier["minimum_lifetime_spend"])) * 100
            )
        else:
            needed = Decimal("0.00")
            progress_pct = 100

        return Response({
            "lifetime_spend": str(lifetime_spend),
            "current_tier": current_tier,
            "next_tier": next_tier,
            "spend_needed_for_next": str(needed.quantize(Decimal("0.01"))),
            "progress_pct": min(progress_pct, 100),
            "tiers": tier_list,
        })

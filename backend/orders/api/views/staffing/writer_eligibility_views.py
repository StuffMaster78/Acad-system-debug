from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models.orders.order import Order
from orders.selectors.writer_eligibility_selector import WriterEligibilitySelector
from orders.services.writer_scope_pricing_service import WriterScopePricingService


class WriterOrderEligibilityView(APIView):
    """
    GET /api/v1/orders/orders/<order_id>/eligibility/

    Returns whether the requesting writer can take or bid on this order,
    plus a level-based suggested bid price and per-unit rate breakdown.
    Used by the pool UI to gate buttons and pre-populate the bid form.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, order_id: int, *args: Any, **kwargs: Any) -> Response:
        from writer_management.utils import get_writer_profile
        from writer_management.models.configs import WriterConfig

        user = cast(Any, request.user)
        website = getattr(request, "website", None) or getattr(user, "website", None)

        order = get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=website,
        )

        try:
            writer = get_writer_profile(user)
        except Exception:
            return Response(
                {"detail": "Writer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Site-level config
        config = WriterConfig.objects.filter(website=website).first()
        takes_enabled = getattr(config, "takes_enabled", True)
        bidding_enabled = True  # always allowed when not takes-enabled

        # Writer capacity
        level = getattr(getattr(writer, "writer_level", None), "settings", None)
        max_active = int(getattr(level, "max_active_orders", 0) or 0) or 999
        active_count = WriterEligibilitySelector.active_orders_for_writer(
            writer=writer,
        ).count()

        snapshot = WriterEligibilitySelector.build_snapshot(
            writer=writer,
            order=order,
            active_order_count=active_count,
            max_active_orders=max_active,
            takes_enabled=takes_enabled,
            bidding_enabled=bidding_enabled,
        )

        suggested_price = WriterScopePricingService.suggested_bid_price(
            writer=writer,
            order=order,
        )
        rates = WriterScopePricingService.rate_breakdown(writer=writer)

        return Response({
            "can_take": snapshot.can_take,
            "can_bid": snapshot.can_bid,
            "has_capacity": snapshot.has_capacity,
            "reason": snapshot.reason,
            "suggested_bid_price": str(suggested_price) if suggested_price else None,
            "rate_breakdown": rates,
        })

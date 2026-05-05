from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from discounts.models.discount_usage import DiscountUsage
from discounts.services.discount_resolution_service import (
    DiscountResolutionService,
)
from discounts.services.discount_usage_service import DiscountUsageService


class DiscountApplicationService:
    """
    Preview or apply one discount to a payable object.

    This is the main orchestration service for client checkout discount
    behavior. Domain apps should call this service instead of creating
    DiscountUsage records directly.
    """

    @staticmethod
    def preview(
        *,
        website,
        client,
        subtotal: Decimal,
        payable_type: str,
        has_prior_paid_purchase: bool,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
    ):
        """
        Resolve a discount without creating usage.

        Preview is informational only. The apply flow must re-resolve the
        discount because limits, expiry, and eligibility can change between
        preview and payment.
        """
        lifetime_spend = lifetime_spend or Decimal("0.00")

        return DiscountResolutionService.resolve(
            website=website,
            client=client,
            subtotal=subtotal,
            payable_type=payable_type,
            has_prior_paid_purchase=has_prior_paid_purchase,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
        )

    @staticmethod
    @transaction.atomic
    def apply(
        *,
        website,
        client,
        subtotal: Decimal,
        payable_type: str,
        payable_id: str,
        has_prior_paid_purchase: bool,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DiscountUsage | None:
        """
        Re-resolve and persist the winning discount usage.

        This method is idempotent per website, payable type, and payable ID.
        If a discount was already applied to the payable item, the existing
        usage record is returned.
        """
        lifetime_spend = lifetime_spend or Decimal("0.00")
        payable_id = str(payable_id)

        existing = DiscountUsage.objects.filter(
            website=website,
            payable_type=payable_type,
            payable_id=payable_id,
        ).first()

        if existing:
            return existing

        resolved = DiscountResolutionService.resolve(
            website=website,
            client=client,
            subtotal=subtotal,
            payable_type=payable_type,
            has_prior_paid_purchase=has_prior_paid_purchase,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
        )

        if resolved is None:
            return None

        return DiscountUsageService.create_usage(
            website=website,
            client=client,
            resolved_discount=resolved,
            subtotal=subtotal,
            payable_type=payable_type,
            payable_id=payable_id,
            metadata=metadata,
        )
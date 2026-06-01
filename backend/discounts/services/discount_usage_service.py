from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import IntegrityError
from django.db import transaction

from discounts.exceptions import DiscountAlreadyAppliedError
from discounts.exceptions import DiscountValidationError
from discounts.models.discount import Discount
from discounts.models.discount_usage import DiscountUsage
from discounts.selectors.discount_usage_selectors import (
    DiscountUsageSelector,
)
from discounts.services.discount_validation_service import (
    DiscountValidationService,
)
from discounts.services.discount_notification_service import (
    DiscountNotificationService,
)

class DiscountUsageService:
    """
    Create immutable discount usage records safely.
    """

    @staticmethod
    @transaction.atomic
    def create_usage(
        *,
        website,
        client,
        resolved_discount,
        subtotal: Decimal,
        payable_type: str,
        payable_id: str,
        lifetime_spend: Decimal | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DiscountUsage:
        """
        Create a usage record for a payable object.

        The discount row is locked before limit validation. This reduces
        race conditions for limited-use discounts.
        """
        lifetime_spend = lifetime_spend or Decimal("0.00")
        payable_id = str(payable_id)

        discount = resolved_discount.discount

        if not isinstance(discount, Discount):
            raise DiscountValidationError(
                "A persisted discount is required."
            )

        if discount.website.id != website.id:
            raise DiscountValidationError(
                "Cross tenant discount usage is not allowed."
            )

        if getattr(client, "website_id", None) != website.id:
            raise DiscountValidationError(
                "Cross tenant client usage is not allowed."
            )

        locked_discount = Discount.objects.select_for_update().get(
            id=discount.pk,
            website=website,
        )

        DiscountValidationService.validate_for_client(
            discount=locked_discount,
            website=website,
            client=client,
            subtotal=subtotal,
            lifetime_spend=lifetime_spend,
        )

        if DiscountUsageSelector.exists_for_payable(
            website=website,
            payable_type=payable_type,
            payable_id=payable_id,
        ):
            raise DiscountAlreadyAppliedError(
                "This payable item already has a discount."
            )

        try:
            usage = DiscountUsage.objects.create(
                website=website,
                discount=locked_discount,
                client=client,
                payable_type=payable_type,
                payable_id=payable_id,
                discount_code=resolved_discount.discount_code,
                discount_type=resolved_discount.discount_type,
                discount_value=resolved_discount.discount_value,
                subtotal_amount=subtotal,
                discount_amount=resolved_discount.discount_amount,
                final_amount=resolved_discount.final_amount,
                origin=resolved_discount.origin,
                metadata=metadata or {},
            )
            DiscountNotificationService.notify_discount_applied(
                usage=usage,
            )

            return usage

        except IntegrityError as exc:
            raise DiscountAlreadyAppliedError(
                "This payable item already has a discount."
            ) from exc
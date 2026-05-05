from __future__ import annotations

from decimal import Decimal
from typing import Any

from discounts.exceptions import DiscountConfigurationError
from discounts.models import DiscountConversionEventLog


class DiscountConversionService:
    """
    Track discount funnel events for dashboard insights.
    """

    @staticmethod
    def record_event(
        *,
        website,
        event: str,
        discount=None,
        client=None,
        payable_type: str = "",
        payable_id: str = "",
        discount_code: str = "",
        subtotal_amount: Decimal = Decimal("0.00"),
        discount_amount: Decimal = Decimal("0.00"),
        final_amount: Decimal = Decimal("0.00"),
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> DiscountConversionEventLog:
        """
        Create a discount conversion event.

        Conversion logs are analytical records. They should never decide
        whether a discount is valid, but they must stay tenant-safe.
        """
        DiscountConversionService._validate_tenant_context(
            website=website,
            discount=discount,
            client=client,
        )

        if discount and not discount_code:
            discount_code = discount.discount_code

        return DiscountConversionEventLog.objects.create(
            website=website,
            discount=discount,
            client=client,
            event=event,
            payable_type=payable_type,
            payable_id=str(payable_id) if payable_id else "",
            discount_code=discount_code,
            subtotal_amount=subtotal_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            reason=reason,
            metadata=metadata or {},
        )

    @staticmethod
    def _validate_tenant_context(
        *,
        website,
        discount=None,
        client=None,
    ) -> None:
        """
        Ensure event objects belong to the same tenant.
        """
        if not website or not getattr(website, "id", None):
            raise DiscountConfigurationError(
                "A valid website is required."
            )

        if (
            discount is not None
            and getattr(discount, "website_id", None) != website.id
        ):
            raise DiscountConfigurationError(
                "Discount does not belong to this website."
            )

        if (
            client is not None
            and getattr(client, "website_id", None) != website.id
        ):
            raise DiscountConfigurationError(
                "Client does not belong to this website."
            )
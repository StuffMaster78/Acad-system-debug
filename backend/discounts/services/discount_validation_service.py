from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from discounts.exceptions import DiscountValidationError
from discounts.selectors.discount_usage_selectors import (
    DiscountUsageSelector,
)
from websites.models.websites import Website


class DiscountValidationService:
    """
    Validate whether a client can use a discount.
    """

    @classmethod
    def validate_for_client(
        cls,
        *,
        discount,
        website,
        client,
        subtotal: Decimal,
        lifetime_spend: Decimal | None = None,
        has_prior_paid_purchase: bool | None = None,
    ):
        """
        Validate a discount for a tenant, client, and subtotal.
        """
        lifetime_spend = lifetime_spend or Decimal("0.00")

        cls._validate_tenant(discount=discount, website=website)
        cls._validate_client_tenant(client=client, website=website)
        cls._validate_enabled(discount=discount)
        cls._validate_campaign(discount=discount)
        cls._validate_time_window(discount=discount)
        cls._validate_minimum(discount=discount, subtotal=subtotal)
        cls._validate_spend_tier(
            discount=discount,
            lifetime_spend=lifetime_spend,
        )
        cls._validate_total_usage_limit(
            website=website,
            discount=discount,
        )
        cls._validate_client_usage_limit(
            website=website,
            discount=discount,
            client=client,
        )
        cls._validate_client_eligibility(
            discount=discount,
            client=client,
        )
        cls._validate_first_order(
            discount=discount,
            has_prior_paid_purchase=has_prior_paid_purchase,
        )

        return discount

    @staticmethod
    def _validate_tenant(*, discount, website) -> None:
        """
        Ensure the discount belongs to the current tenant.
        """
        if discount.website_id != website.id:
            raise DiscountValidationError(
                "This discount does not belong to this website."
            )

    @staticmethod
    def _validate_client_tenant(*, client, website) -> None:
        """
        Ensure the client belongs to the current tenant.
        """
        if getattr(client, "website_id", None) != website.id:
            raise DiscountValidationError(
                "This client does not belong to this website."
            )

    @staticmethod
    def _validate_enabled(*, discount) -> None:
        """
        Ensure the discount can currently be used.
        """
        if not discount.is_active:
            raise DiscountValidationError("This discount is inactive.")

        if discount.is_archived:
            raise DiscountValidationError("This discount is archived.")

        if discount.is_deleted:
            raise DiscountValidationError("This discount is deleted.")

    @staticmethod
    def _validate_campaign(*, discount) -> None:
        """
        Ensure linked campaign is usable.
        """
        campaign = discount.campaign

        if campaign is None:
            return

        if campaign.is_archived:
            raise DiscountValidationError(
                "This discount campaign is archived."
            )

        if not campaign.is_active:
            raise DiscountValidationError(
                "This discount campaign is inactive."
            )
        
    @staticmethod
    def _validate_time_window(*, discount) -> None:
        """
        Ensure the discount is within its active time window.
        """
        now = timezone.now()

        if discount.starts_at and discount.starts_at > now:
            raise DiscountValidationError(
                "This discount is not active yet."
            )

        if discount.ends_at and discount.ends_at < now:
            raise DiscountValidationError("This discount has expired.")

    @staticmethod
    def _validate_minimum(*, discount, subtotal: Decimal) -> None:
        """
        Ensure the subtotal meets the minimum payable amount.
        """
        if subtotal < discount.min_payable_amount:
            raise DiscountValidationError(
                "This discount requires a higher subtotal."
            )

    @staticmethod
    def _validate_spend_tier(
        *,
        discount,
        lifetime_spend: Decimal,
    ) -> None:
        """
        Ensure spend-tier discounts require enough client lifetime spend.
        """
        tier = getattr(discount, "spend_tier", None)

        if tier is None:
            return

        if lifetime_spend < tier.minimum_lifetime_spend:
            raise DiscountValidationError(
                "You are not eligible for this tier discount."
            )

    @staticmethod
    def _validate_total_usage_limit(*, website, discount) -> None:
        """
        Ensure the global usage limit has not been reached.
        """
        if discount.usage_limit is None:
            return

        usage_count = DiscountUsageSelector.count_for_discount(
            website=website,
            discount=discount,
        )

        if usage_count >= discount.usage_limit:
            raise DiscountValidationError(
                "This discount has reached its usage limit."
            )

    @staticmethod
    def _validate_client_usage_limit(*, website, discount, client) -> None:
        """
        Ensure the client usage limit has not been reached.
        """
        if discount.per_client_usage_limit is None:
            return

        usage_count = DiscountUsageSelector.count_for_client_discount(
            website=website,
            discount=discount,
            client=client,
        )

        if usage_count >= discount.per_client_usage_limit:
            raise DiscountValidationError(
                "You have already used this discount."
            )

    @staticmethod
    def _validate_client_eligibility(*, discount, client) -> None:
        """
        Ensure targeted discounts only apply to eligible clients.
        """
        if not discount.eligible_clients.exists():
            return

        is_eligible = discount.eligible_clients.filter(
            id=client.id,
            website_id=discount.website_id,
        ).exists()

        if not is_eligible:
            raise DiscountValidationError(
                "You are not eligible for this discount."
            )
        
    @staticmethod
    def _validate_first_order(
        *,
        discount,
        has_prior_paid_purchase: bool | None,
    ) -> None:
        """
        Ensure first-order discounts are only used by new clients.
        """
        if not discount.first_order_only:
            return

        if has_prior_paid_purchase:
            raise DiscountValidationError(
                "This discount is only valid for first orders."
            )
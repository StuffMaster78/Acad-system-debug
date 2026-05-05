from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from discounts.constants import DiscountOrigin
from discounts.exceptions import DiscountConfigurationError
from discounts.models.discount_spend_tier import DiscountSpendTier
from discounts.services.discount_admin_service import DiscountAdminService
from discounts.services.discount_code_generator import DiscountCodeGenerator


class DiscountSpendTierAdminService:
    """
    Admin write service for spend-based discount tiers.
    """

    @staticmethod
    @transaction.atomic
    def create_tier(
        *,
        website,
        name: str,
        discount_code: str,
        discount_type: str,
        discount_value: Decimal,
        minimum_lifetime_spend: Decimal,
        created_by=None,
        description: str = "",
        max_discount_amount: Decimal | None = None,
        usage_limit: int | None = None,
        per_client_usage_limit: int | None = None,
        is_active: bool = True,
        is_campaign_managed: bool = True,
    ) -> DiscountSpendTier:
        """
        Create a spend tier and its linked discount code.
        """
        DiscountSpendTierAdminService._validate_website(website=website)
        DiscountSpendTierAdminService._validate_minimum_spend(
            minimum_lifetime_spend=minimum_lifetime_spend,
        )

        normalized_code = DiscountCodeGenerator.normalize(discount_code)

        DiscountSpendTierAdminService._validate_unique_code(
            website=website,
            discount_code=normalized_code,
        )

        discount = DiscountAdminService.create_discount(
            website=website,
            name=name,
            discount_code=normalized_code,
            description=description,
            discount_type=discount_type,
            discount_value=discount_value,
            max_discount_amount=max_discount_amount,
            usage_limit=usage_limit,
            per_client_usage_limit=per_client_usage_limit,
            origin=DiscountOrigin.SPEND_TIER,
            is_active=is_active,
            is_campaign_managed=is_campaign_managed,
            created_by=created_by,
        )

        return DiscountSpendTier.objects.create(
            website=website,
            discount=discount,
            name=name,
            minimum_lifetime_spend=minimum_lifetime_spend,
            is_active=is_active,
            created_by=created_by,
            updated_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def update_tier(
        *,
        tier: DiscountSpendTier,
        updated_by=None,
        **fields: Any,
    ) -> DiscountSpendTier:
        """
        Update a spend tier and selected linked discount fields.
        """
        DiscountSpendTierAdminService._validate_website(
            website=tier.website,
        )

        if "minimum_lifetime_spend" in fields:
            DiscountSpendTierAdminService._validate_minimum_spend(
                minimum_lifetime_spend=fields["minimum_lifetime_spend"],
            )

        discount = tier.discount

        if "discount_code" in fields:
            normalized_code = DiscountCodeGenerator.normalize(
                fields["discount_code"],
            )
            DiscountSpendTierAdminService._validate_unique_code(
                website=tier.website,
                discount_code=normalized_code,
                current_discount_id=discount.id,
            )
            fields["discount_code"] = normalized_code

        tier_fields = {
            "name",
            "minimum_lifetime_spend",
            "is_active",
        }
        discount_fields = {
            "discount_code",
            "discount_type",
            "discount_value",
            "description",
            "max_discount_amount",
            "usage_limit",
            "per_client_usage_limit",
            "is_active",
            "is_campaign_managed",
        }

        for field, value in fields.items():
            if field in tier_fields:
                setattr(tier, field, value)

            if field in discount_fields:
                setattr(discount, field, value)

        discount.updated_by = updated_by
        discount.save()

        tier.updated_by = updated_by
        tier.save()

        return tier

    @staticmethod
    def _validate_website(*, website) -> None:
        """
        Ensure a valid tenant website exists.
        """
        if not website or not getattr(website, "id", None):
            raise DiscountConfigurationError(
                "A valid website is required."
            )

    @staticmethod
    def _validate_minimum_spend(
        *,
        minimum_lifetime_spend: Decimal,
    ) -> None:
        """
        Ensure tier minimum spend is not negative.
        """
        if minimum_lifetime_spend < Decimal("0.00"):
            raise DiscountConfigurationError(
                "Minimum lifetime spend cannot be negative."
            )

    @staticmethod
    def _validate_unique_code(
        *,
        website,
        discount_code: str,
        current_discount_id: int | None = None,
    ) -> None:
        """
        Ensure tier discount code is unique within a website.
        """
        from discounts.models.discount import Discount

        queryset = Discount.objects.filter(
            website=website,
            discount_code=discount_code,
        )

        if current_discount_id is not None:
            queryset = queryset.exclude(id=current_discount_id)

        if queryset.exists():
            raise DiscountConfigurationError(
                "A discount with this code already exists."
            )
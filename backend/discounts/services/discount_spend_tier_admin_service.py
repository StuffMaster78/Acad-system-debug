from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from discounts.constants import DiscountOrigin
from discounts.models import DiscountSpendTier
from discounts.services.discount_admin_service import DiscountAdminService


class DiscountSpendTierAdminService:
    """
    Admin write service for spend based discount tiers.
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
    ) -> DiscountSpendTier:
        """
        Create a spend tier and its linked discount code.
        """
        discount = DiscountAdminService.create_discount(
            website=website,
            name=name,
            discount_code=discount_code,
            description=description,
            discount_type=discount_type,
            discount_value=discount_value,
            max_discount_amount=max_discount_amount,
            usage_limit=usage_limit,
            per_client_usage_limit=per_client_usage_limit,
            origin=DiscountOrigin.SPEND_TIER,
            is_active=is_active,
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
        **fields,
    ) -> DiscountSpendTier:
        """
        Update a spend tier and selected linked discount fields.
        """
        discount_fields = {
            "discount_code",
            "discount_type",
            "discount_value",
            "description",
            "max_discount_amount",
            "usage_limit",
            "per_client_usage_limit",
            "is_active",
        }

        discount = tier.discount

        for field, value in fields.items():
            if field in {"name", "minimum_lifetime_spend", "is_active"}:
                setattr(tier, field, value)

            if field in discount_fields:
                setattr(discount, field, value)

        discount.updated_by = updated_by
        discount.save()

        tier.updated_by = updated_by
        tier.save()

        return tier
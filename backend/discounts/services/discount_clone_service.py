from __future__ import annotations

from django.db import transaction
from django.utils.text import slugify

from discounts.exceptions import DiscountConfigurationError
from discounts.models.discount import Discount
from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.services.discount_admin_service import DiscountAdminService
from discounts.services.discount_code_generator import DiscountCodeGenerator


class DiscountCloneService:
    """
    Clone campaigns and discounts across websites.
    """

    @staticmethod
    @transaction.atomic
    def clone_discount(
        *,
        source_discount: Discount,
        target_website,
        created_by=None,
        new_code: str | None = None,
        target_campaign=None,
    ) -> Discount:
        """
        Clone one discount into another website.
        """
        DiscountCloneService._validate_campaign_tenant(
            target_website=target_website,
            target_campaign=target_campaign,
        )

        code = new_code or DiscountCodeGenerator.generate_unique(
            website=target_website,
            prefix=source_discount.discount_code,
        )
        code = DiscountCodeGenerator.normalize(code)

        DiscountCloneService._validate_code_unique(
            target_website=target_website,
            code=code,
        )

        return DiscountAdminService.create_discount(
            website=target_website,
            campaign=target_campaign,
            name=source_discount.name,
            description=source_discount.description,
            discount_code=code,
            discount_type=source_discount.discount_type,
            discount_value=source_discount.discount_value,
            max_discount_amount=source_discount.max_discount_amount,
            min_payable_amount=source_discount.min_payable_amount,
            starts_at=source_discount.starts_at,
            ends_at=source_discount.ends_at,
            usage_limit=source_discount.usage_limit,
            per_client_usage_limit=(
                source_discount.per_client_usage_limit
            ),
            first_order_only=source_discount.first_order_only,
            origin=source_discount.origin,
            is_active=source_discount.is_active,
            is_campaign_managed = (
                source_discount.is_campaign_managed
                if target_campaign is None
                else True
            ),
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def clone_campaign(
        *,
        source_campaign: PromotionalCampaign,
        target_website,
        created_by=None,
        new_name: str | None = None,
        new_slug: str | None = None,
    ) -> PromotionalCampaign:
        """
        Clone a campaign and its discounts into another website.
        """
        name = new_name or source_campaign.name
        slug = DiscountCloneService._resolve_unique_campaign_slug(
            target_website=target_website,
            raw_slug=new_slug or source_campaign.slug,
        )

        campaign = PromotionalCampaign.objects.create(
            website=target_website,
            name=name,
            slug=slug,
            description=source_campaign.description,
            starts_at=source_campaign.starts_at,
            ends_at=source_campaign.ends_at,
            is_active=source_campaign.is_active,
            is_archived=False,
            created_by=created_by,
            updated_by=created_by,
        )

        source_discounts = Discount.objects.filter(
            campaign=source_campaign,
            is_deleted=False,
        )

        for discount in source_discounts:
            DiscountCloneService.clone_discount(
                source_discount=discount,
                target_website=target_website,
                created_by=created_by,
                target_campaign=campaign,
            )

        return campaign

    @staticmethod
    def _validate_campaign_tenant(
        *,
        target_website,
        target_campaign,
    ) -> None:
        """
        Ensure target campaign belongs to the target website.
        """
        if target_campaign is None:
            return

        if target_campaign.website_id != target_website.id:
            raise DiscountConfigurationError(
                "Target campaign does not belong to target website."
            )

    @staticmethod
    def _validate_code_unique(*, target_website, code: str) -> None:
        """
        Ensure discount code is unique within target website.
        """
        if Discount.objects.filter(
            website=target_website,
            discount_code=code,
        ).exists():
            raise DiscountConfigurationError(
                "Discount code already exists for target website."
            )

    @staticmethod
    def _resolve_unique_campaign_slug(
        *,
        target_website,
        raw_slug: str,
    ) -> str:
        """
        Return a campaign slug unique within target website.
        """
        base_slug = slugify(raw_slug) or "campaign"
        candidate = base_slug
        counter = 1

        while PromotionalCampaign.objects.filter(
            website=target_website,
            slug=candidate,
        ).exists():
            counter += 1
            candidate = f"{base_slug}-{counter}"

        return candidate
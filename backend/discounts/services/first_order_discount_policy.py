from __future__ import annotations

from decimal import Decimal

from discounts.constants import PayableType
from discounts.models.first_order_discount_config import (
    FirstOrderDiscountConfig,
)


class FirstOrderDiscountPolicy:
    """
    Resolve automatic first order discount eligibility.
    """

    @classmethod
    def get_discount(
        cls,
        *,
        website,
        payable_type: str,
        has_prior_paid_purchase: bool,
        created_by=None,
    ):
        """
        Return a persisted first order discount when applicable.
        """
        if has_prior_paid_purchase:
            return None

        config = cls._get_enabled_config(website=website)

        if config is None:
            return None

        if not cls._applies_to_payable_type(
            config=config,
            payable_type=payable_type,
        ):
            return None

        if config.discount_value <= Decimal("0.00"):
            return None

        from discounts.services.discount_admin_service import (
            DiscountAdminService,
        )

        return DiscountAdminService.get_or_create_first_order_discount(
            website=website,
            config=config,
            created_by=created_by,
        )

    @staticmethod
    def _get_enabled_config(*, website) -> FirstOrderDiscountConfig | None:
        """
        Return enabled first order config for a website.
        """
        return FirstOrderDiscountConfig.objects.filter(
            website=website,
            is_enabled=True,
        ).first()

    @staticmethod
    def _applies_to_payable_type(
        *,
        config: FirstOrderDiscountConfig,
        payable_type: str,
    ) -> bool:
        """
        Return whether the config applies to the payable type.
        """
        if payable_type == PayableType.ORDER:
            return config.applies_to_orders

        if payable_type == PayableType.SPECIAL_ORDER:
            return config.applies_to_special_orders

        if payable_type == PayableType.CLASS_ORDER:
            return config.applies_to_class_bundles

        return False
import logging
import random
import string
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db import transaction

from orders.utils.order_utils import get_order_by_id
from typing import List, Dict, Any
# from notifications_system.services.dispatcher import notify_user
from discounts.utils import get_discount_model
from discounts.services.discount_generator import DiscountCodeGenerator

logger = logging.getLogger(__name__)
# Ensure we have the correct model loaded



class DiscountCodeService:
    """
    Service to generate discount codes for admins.

    Supports promotional campaigns, client-specific codes,
    or general codes.
    """

    @staticmethod
    def generate_code(prefix='', length=6):
        """
        Proxy method to generate a globally unique discount code with an optional prefix.
        Args:
            prefix (str): Optional code prefix (e.g., 'WELCOME2025').
            length (int): Length of the random suffix.
        Returns:
            str: A unique discount code.
        Raises:
            RuntimeError: If unable to generate a unique code after multiple attempts.
        """
        return DiscountCodeGenerator.generate_unique_code(prefix=prefix, length=length)


    @classmethod
    def create_discount_code(
        cls,
        *,
        code=None,
        discount_type='percent',
        discount_value,
        start_date,
        end_date,
        usage_limit=None,
        website=None,
        promotional_campaign=None,
        client=None,
        is_active=True,
    ):
        """
        Create a discount code with optional ties to promotional campaign or client.

        Returns:
            Discount: Created Discount instance.

        Raises:
            ValidationError: For invalid data or conflicts.
        """
        from discounts.models import Discount
        if start_date >= end_date:
            raise ValidationError("End date must be after start date.")

        if discount_type == 'percent':
            if discount_value <= 0 or discount_value > 100:
                raise ValidationError(
                    "Percent discount must be > 0 and <= 100."
                )
        elif discount_type == 'fixed':
            if discount_value <= 0:
                raise ValidationError("Fixed discount must be greater than zero.")
        else:
            raise ValidationError("discount_type must be 'percent' or 'fixed'.")

        if promotional_campaign:
            if not promotional_campaign.is_active:
                raise ValidationError(
                    "Cannot attach discount to inactive promotional campaign."
                )
            if start_date < promotional_campaign.start_date or end_date > \
                    promotional_campaign.end_date:
                raise ValidationError(
                    "Discount validity must be within promotional campaign dates."
                )
            if website and promotional_campaign.website != website:
                raise ValidationError(
                    "Promotional campaign does not belong to given website."
                )

        # 🔁 Code generation moved to service
        if not code:
            prefix = getattr(promotional_campaign, 'code_prefix', 'DISC')
            try:
                code = DiscountCodeGenerator.generate_unique_code(prefix=prefix)
            except RuntimeError as e:
                raise ValidationError(str(e))

        if Discount.objects.filter(code=code).exists():
            raise ValidationError(f"Discount code '{code}' already exists.")

        with transaction.atomic():
            discount = Discount.objects.create(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                start_date=start_date,
                end_date=end_date,
                usage_limit=usage_limit,
                website=website,
                promotional_campaign=promotional_campaign,
                assigned_to_client=client,
                client=client,
                is_active=is_active,
                used_count=0,
            )
        return discount

    @staticmethod
    def deactivate_code(discount):
        """
        Deactivate a discount code.

        Args:
            discount (Discount): The discount instance.

        Returns:
            Discount: Updated discount instance.
        """
        discount.is_active = False
        discount.save(update_fields=['is_active'])
        return discount
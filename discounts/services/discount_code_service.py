import logging
import random
import string
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db import transaction

from discounts.models import Discount
from orders.utils.order_utils import get_order_by_id
from typing import List, Dict, Any
from discounts.services.discount_suggestions import DiscountSuggestionService
from discounts.services.discount_engine import DiscountEngine
from discounts.services.discount_hints import DiscountHintService
from notifications_system.services import notify_admin_of_error
from discounts.utils import get_discount_model

logger = logging.getLogger(__name__)
# Ensure we have the correct model loaded
Discount = get_discount_model()


class DiscountCodeService:
    """
    Service to generate discount codes for admins.

    Supports seasonal events, client-specific codes,
    or general codes.
    """

    @staticmethod
    def generate_code(prefix='DISC', length=6):
        """
        Generate a unique uppercase discount code with prefix.

        Args:
            prefix (str): Prefix for the code. Defaults to 'DISC'.
            length (int): Length of random suffix. Defaults to 6.

        Returns:
            str: Generated discount code in format PREFIX-XXXXXX.
        """
        suffix = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=length)
        )
        return f"{prefix.upper()}-{suffix}"

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
        Create a discount code with optional ties to event or client.

        Args:
            code (str): Optional exact code. Generated if None.
            discount_type (str): 'percent' or 'fixed'.
            discount_value (Decimal): Discount amount.
            start_date (datetime): Discount valid start datetime.
            end_date (datetime): Discount valid end datetime.
            usage_limit (int|None): Max allowed uses.
            website (Website|None): Website for the discount.
            seasonal_event (SeasonalEvent|None): Event to link.
            client (User|None): User to restrict discount.
            is_active (bool): If discount is active.

        Returns:
            Discount: Created Discount instance.

        Raises:
            ValidationError: For invalid data or conflicts.
        """
        if start_date >= end_date:
            raise ValidationError("End date must be after start date.")

        if discount_type == 'percent':
            if discount_value <= 0 or discount_value > 100:
                raise ValidationError(
                    "Percent discount must be > 0 and <= 100."
                )
        elif discount_type == 'fixed':
            if discount_value <= 0:
                raise ValidationError(
                    "Fixed discount must be greater than zero."
                )
        else:
            raise ValidationError(
                "discount_type must be 'percent' or 'fixed'."
            )

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

        if not code:
            prefix = getattr(promotional_campaign, 'code_prefix', 'DISC')
            for _ in range(10):
                candidate = cls.generate_code(prefix=prefix)
                if not DiscountEngine.fetch_by_codes(code=candidate).exists():
                    code = candidate
                    break
            else:
                raise ValidationError(
                    "Failed to generate unique discount code after 10 tries."
                )

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
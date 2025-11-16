import random
import string
import logging

from django.db import transaction
from django.core.exceptions import ValidationError
logger = logging.getLogger(__name__)



class DiscountCodeGenerator:
    """
    Generates globally unique discount codes with optional prefixing.

    Usage:
        DiscountCodeGenerator.generate_unique_code(prefix="FALL2025")
    """

    DEFAULT_LENGTH = 6
    MAX_ATTEMPTS = 10
    CHARSET = string.ascii_uppercase + string.digits
    MAX_CODE_LENGTH = 15

    @classmethod
    def generate_unique_code(cls, prefix: str = '', length: int = None) -> str:
        """
        Generate a unique discount code with optional prefix.

        Args:
            prefix (str): Optional prefix for the code (e.g., "SUMMER").
            length (int): Length of the random suffix. Defaults to 6.

        Returns:
            str: A unique discount code.

        Raises:
            RuntimeError: If unable to generate a unique code.
        """
        from discounts.models import Discount
        length = length or cls.DEFAULT_LENGTH

        # Truncate prefix if needed to fit code within max length
        prefix = prefix.strip().upper().replace(' ', '_')
        max_prefix_len = cls.MAX_CODE_LENGTH - length
        if len(prefix) > max_prefix_len:
            prefix = prefix[:max_prefix_len]

        for attempt in range(cls.MAX_ATTEMPTS):
            suffix = ''.join(random.choices(cls.CHARSET, k=length))
            prefix = prefix[:max_prefix_len]    
            candidate = f"{prefix}_{suffix}" if prefix else suffix.upper()
            if not Discount.objects.filter(discount_code=candidate).exists():
                return candidate

        logger.error(
            f"Failed to generate unique code after {cls.MAX_ATTEMPTS} attempts. "
            f"Prefix used: '{prefix}'"
        )
        raise RuntimeError("Unable to generate unique discount code.")


    @classmethod
    def bulk_create_discounts(
        cls,
        *,
        prefix: str,
        total: int,
        discount_type: str,
        discount_value,
        start_date,
        end_date,
        usage_limit=None,
        website=None,
        promotional_campaign=None,
        client=None,
        is_active=True,
        code_length: int = 6
    ) -> list:
        """
        Bulk generate discount codes and create Discount objects.

        Args:
            prefix (str): Prefix for codes.
            total (int): Number of codes to generate.
            discount_type (str): 'percent' or 'fixed'.
            discount_value (Decimal): Discount amount.
            start_date (datetime): Discount validity start.
            end_date (datetime): Discount validity end.
            usage_limit (int|None): Max uses.
            website (Website|None): Optional website scope.
            promotional_campaign (PromotionalCampaign|None): Optional campaign.
            client (User|None): Assign to a client.
            is_active (bool): Set discount as active.
            code_length (int): Length of random suffix.

        Returns:
            List[Discount]: Created discount instances.
        """
        from discounts.models import Discount
        if discount_type not in ['percent', 'fixed']:
            raise ValidationError("discount_type must be 'percent' or 'fixed'.")

        if discount_type == 'percent' and (discount_value <= 0 or discount_value > 100):
            raise ValidationError("Percent discount must be > 0 and <= 100.")
        elif discount_type == 'fixed' and discount_value <= 0:
            raise ValidationError("Fixed discount must be > 0.")

        if start_date >= end_date:
            raise ValidationError("End date must be after start date.")

        if promotional_campaign:
            if not promotional_campaign.is_active:
                raise ValidationError("Campaign must be active.")
            if start_date < promotional_campaign.start_date or \
               end_date > promotional_campaign.end_date:
                raise ValidationError("Discount validity must fall within campaign.")
            if website and promotional_campaign.website != website:
                raise ValidationError("Campaign doesn't match website.")

        codes = set()
        discounts = []

        for _ in range(total):
            code = DiscountCodeGenerator.generate_unique_code(
                prefix=prefix,
                length=code_length
            )
            if code in codes:
                continue
            codes.add(code)

        with transaction.atomic():
            for code in codes:
                discount = Discount.objects.create(
                    discount_code=code,
                    discount_type=discount_type,
                    discount_value=discount_value,
                    start_date=start_date,
                    end_date=end_date,
                    usage_limit=usage_limit,
                    website=website,
                    promotional_campaign=promotional_campaign,
                    assigned_to_client=client,
                    is_active=is_active,
                    origin_type='promo' if promotional_campaign else 'manual',
                    used_count=0
                )
                discounts.append(discount)

        return discounts
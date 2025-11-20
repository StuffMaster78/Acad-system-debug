"""
Service to duplicate discount codes with reset values.
"""

import string
import random
from copy import deepcopy
from typing import List

from django.utils.timezone import now
from discounts.utils import get_discount_model


class DiscountCloningService:
    """
    Handles the duplication of discount objects for reuse or promotions.
    """

    @staticmethod
    def duplicate_discounts(queryset) -> List:
        """
        Duplicate a queryset of discounts with reset fields.

        Args:
            queryset (QuerySet): The discounts to clone.

        Returns:
            list: List of newly created, unsaved Discount instances.
        """
        new_discounts = []
        for discount in queryset:
            clone = deepcopy(discount)
            clone.pk = None
            clone.code += "_" + ''.join(random.choices(string.ascii_uppercase, k=4))
            clone.start_date = now()
            clone.end_date = None
            clone.is_active = True
            clone.used_count = 0
            new_discounts.append(clone)
        return new_discounts
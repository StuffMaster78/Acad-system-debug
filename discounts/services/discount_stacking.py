"""
Advanced discount stacking service with support for:
- stacking flags (allow_stacking)
- exclusive stacking groups
- stacking priority resolution
- explicit DiscountStackingRule matrix
"""

import logging

from rest_framework.exceptions import ValidationError
from django.db.models import Q

from discounts.utils import get_discount_model, get_discount_usage_model
from discounts.models.stacking import DiscountStackingRule

logger = logging.getLogger(__name__)


class DiscountStackingService:
    """
    Validates and resolves discount stacking based on stacking flags,
    stacking groups, priority, and explicit stacking rules.
    """

    def __init__(self, user, website=None):
        """
        Initialize the stacking service.

        Args:
            user (User): The user attempting to apply discounts.
            website (Website, optional): Website context.
        """
        self.user = user
        self.website = website
        self.discount_model = get_discount_model()
        self.usage_model = get_discount_usage_model()
        self.active_discounts = self._get_active_discounts()

    def _get_active_discounts(self):
        """
        Fetch currently applied discounts.

        Returns:
            QuerySet: Active Discount objects.
        """
        usage_qs = self.usage_model.objects.filter(
            user=self.user,
            used=True,
            discount__is_active=True,
        )
        if self.website:
            usage_qs = usage_qs.filter(discount__website=self.website)
        return self.discount_model.objects.filter(
            id__in=usage_qs.values_list("discount_id", flat=True)
        )

    def validate_stacking(self, new_discount):
        """
        Validate whether a new discount can be stacked.

        Args:
            new_discount (Discount): Discount to validate.

        Raises:
            ValidationError: If discount can't be stacked.
        """
        if not self._can_stack(new_discount):
            blockers = self.get_blocking_discounts(new_discount)
            codes = ", ".join(d.discount_code for d in blockers)
            logger.warning(
                f"Stacking violation: {new_discount.discount_code} blocked by {codes}"
            )
            raise ValidationError(
                f"Discount {new_discount.discount_code} cannot be stacked with: {codes}"
            )

    def _can_stack(self, new_discount):
        """
        Internal validation of stacking logic.

        Args:
            new_discount (Discount): Discount to check against active discounts.

        Returns:
            bool: True if stacking allowed.
        """
        # If new discount doesn't allow stacking and there are active discounts, reject
        if not new_discount.allow_stacking and self.active_discounts.exists():
            return False

        # Check campaign restrictions - discounts from different campaigns cannot stack
        # unless allow_stack_across_events is enabled in config
        for active in self.active_discounts:
            if active.promotional_campaign_id and new_discount.promotional_campaign_id:
                if active.promotional_campaign_id != new_discount.promotional_campaign_id:
                    # Check if cross-campaign stacking is allowed
                    if self.website:
                        from discounts.models.discount_configs import DiscountConfig
                        config = DiscountConfig.objects.filter(website=self.website).first()
                        if not config or not config.allow_stack_across_events:
                            return False

        # Check each active discount for conflicts
        for active in self.active_discounts:
            # If any active discount doesn't allow stacking, reject
            if not active.allow_stacking:
                return False

            # Check stacking group conflicts (exclusive groups)
            if (
                new_discount.stacking_group
                and active.stacking_group
                and new_discount.stacking_group == active.stacking_group
            ):
                return False

            # Check explicit stacking rules
            if not self.are_discounts_stackable(active, new_discount):
                return False

        return True

    def get_blocking_discounts(self, new_discount):
        """
        Determine which discounts are blocking stacking.

        Args:
            new_discount (Discount): Discount to analyze.

        Returns:
            list: Blocking Discount objects.
        """
        blockers = []

        if not new_discount.allow_stacking and self.active_discounts.exists():
            blockers.extend(self.active_discounts)

        for active in self.active_discounts:
            if not active.allow_stacking:
                blockers.append(active)
            elif (
                new_discount.stacking_group
                and active.stacking_group
                and new_discount.stacking_group == active.stacking_group
            ):
                blockers.append(active)
            elif not self.are_discounts_stackable(active, new_discount):
                blockers.append(active)

        return blockers

    @staticmethod
    def are_discounts_stackable(discount_a, discount_b):
        """
        Determine if two discounts are allowed to stack based
        on DiscountStackingRule entries.

        Args:
            discount_a (Discount): First discount.
            discount_b (Discount): Second discount.

        Returns:
            bool: True if they are allowed to stack.
        """
        if discount_a.id == discount_b.id:
            return True

        rule_exists = DiscountStackingRule.objects.filter(
            Q(discount=discount_a, stackable_discount=discount_b)
            | Q(discount=discount_b, stackable_discount=discount_a)
        ).exists()
        return rule_exists
    
    def validate_stacking(self):
        """
        Validate if the selected discounts can be stacked together.

        Raises:
            ValueError: If stacking is not allowed.
        """
        for discount in self.discounts:
            if not discount.allow_stack:
                raise ValueError(
                    f"Discount {discount.code} cannot be stacked."
                )

    def resolve_stack_from_list(self, discounts):
        """
        Resolve stacking conflicts from a list of candidate discounts,
        applying priority, stacking rules, exclusivity, and maximum count limits.

        Args:
            discounts (list): List of Discount objects.

        Returns:
            list: Stackable discounts after resolution.
        """
        # Get config to check maximum discount count
        from discounts.models.discount_configs import DiscountConfig
        config = None
        if self.website:
            config = DiscountConfig.objects.filter(website=self.website).first()
        
        max_count = config.max_stackable_discounts if config else 1

        candidates = sorted(
            discounts, key=lambda d: d.stacking_priority or 0, reverse=True
        )
        final_stack = []
        used_groups = set()

        for discount in candidates:
            # Enforce maximum discount count
            if len(final_stack) >= max_count:
                logger.debug(
                    f"Skipping {discount.discount_code} - maximum discount count ({max_count}) reached"
                )
                continue

            if not discount.allow_stacking and final_stack:
                logger.debug(
                    f"Skipping {discount.discount_code} - disallows stacking"
                )
                continue

            if any(not d.allow_stacking for d in final_stack):
                logger.debug(
                    f"Skipping {discount.discount_code} - blocked by no-stack discount"
                )
                continue

            if discount.stacking_group and discount.stacking_group in used_groups:
                logger.debug(
                    f"Skipping {discount.discount_code} - stacking group conflict"
                )
                continue

            # Explicit rule check
            if not all(
                self.are_discounts_stackable(discount, existing)
                for existing in final_stack
            ):
                logger.debug(
                    f"Skipping {discount.discount_code} - rule table conflict"
                )
                continue

            final_stack.append(discount)
            if discount.stacking_group:
                used_groups.add(discount.stacking_group)

        return final_stack
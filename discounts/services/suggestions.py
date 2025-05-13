from django.utils.timezone import now
from discounts.models import Discount
import logging

# Logger setup
logger = logging.getLogger(__name__)

class DiscountSuggestionService:
    """
    Service to provide discount suggestions for a given website.
    Filters discounts based on validity and usage count, with future-proofing.
    """

    @staticmethod
    def get_suggestions(website, limit=3):
        """
        Retrieve top discount suggestions for the given website.
        Filters by active discounts, valid time window, and usage count.
        Sorted by usage count and created date for tie-breaking.

        Args:
            website: The website object to get discounts for.
            limit: Maximum number of discount suggestions to return.

        Returns:
            A list of dictionaries containing discount details.
        """
        current_time = now()

        # Get the queryset of active discounts within the valid time window
        discounts_qs = Discount.objects.filter(
            website=website,
            is_active=True,
            valid_from__lte=current_time,
            valid_until__gte=current_time
        ).order_by('-usage_count', '-created_at')  # Fallback sorting on created_at


        suggestions = list(
            discounts_qs[:limit].values('code', 'description', 'percentage', 'flat_amount')
        )

        # If no discounts are available, log this
        if not discounts_qs.exists():
            logger.info(f"No active discount suggestions found for website: {website.id}")

        # Return the top 'limit' discounts with selected fields
        return suggestions
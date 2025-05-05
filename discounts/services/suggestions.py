from discounts.models import Discount
from datetime import datetime

class DiscountSuggestionService:

    @staticmethod
    def get_suggestions(website, limit=3):
        now = datetime.now()
        return list(
            Discount.objects.filter(
                website=website,
                is_active=True,
                valid_from__lte=now,
                valid_until__gte=now
            )
            .order_by('-usage_count')[:limit]
            .values('code', 'description', 'percentage', 'flat_amount')
        )
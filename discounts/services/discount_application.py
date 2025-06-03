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

class ApplyDiscountCodeService:
    """
    Service to apply discount codes to an order.
    Centralizes discount application logic and handles errors.
    """
    @staticmethod
    @transaction.atomic
    def apply_discounts_to_order(
        order_id: int,
        codes: List[str], user
    ) -> Dict[str, Any]:
        order = get_order_by_id(order_id)
        result = {
            "final_price": float(order.total_price),
            "discounts_applied": [],
            "errors": [],
            "stackable_hint": None,
            "suggested_discounts": [],
            "codes_attempted": codes,
        }
        try:
            # Centralize all logic in DiscountEngine
            final_price, applied_discounts = DiscountEngine.apply_discount_to_order(
                order, codes, order.website, user=user
            )
            result.update({
                "final_price": float(final_price),
                "discounts_applied": applied_discounts,
            })
            hint = DiscountHintService.get_stackable_hint(codes, order.website)
            if hint:
                result["stackable_hint"] = hint
            logger.info(
                f"User {user.id} applied discounts {codes} to order {order.id}, "
                f"final price: {result['final_price']}"
            )
            return result
        except ValidationError as ve:
            order.refresh_from_db()
            logger.warning(f"Discount validation failed for order {order.id}: {ve}")
            suggestions = DiscountSuggestionService.get_suggestions(order.website)
            result.update({
                "errors": [str(ve)],
                "suggested_discounts": suggestions,
            })
            return result
        except Exception as exc:
            logger.exception(f"Critical error applying discounts on order {order.id}: {exc}")
            notify_admin_of_error(f"Discount error on order {order.id}: {exc}")
            suggestions = DiscountSuggestionService.get_suggestions(order.website)
            result.update({
                "errors": ["Unexpected internal error. Please try again later."],
                "suggested_discounts": suggestions,
            })
            return result
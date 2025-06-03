import logging
from typing import List, Dict, Any

from django.db import transaction
from django.core.exceptions import ValidationError

from orders.utils.order_utils import get_order_by_id
from discounts.services import DiscountEngine
from discounts.services.discount_suggestions import   DiscountSuggestionService
from discounts.services.discount_hints import DiscountHintService
from notifications_system.services import notify_admin_of_error
from discounts.services.discount_usage_tracker import DiscountUsageTracker
logger = logging.getLogger(__name__)


class ApplyDiscountCodeService:
    """
    Service for applying one or more discount codes to an order.

    Methods:
        apply_discounts_to_order: Applies discount codes and updates the order.
    """

    @staticmethod
    @transaction.atomic
    def apply_discounts_to_order(
        order_id: int, codes: List[str], user
    ) -> Dict[str, Any]:
        """
        Apply one or more discount codes to an order.

        Args:
            order_id (int): The ID of the order.
            codes (List[str]): Discount codes to apply.
            user: The user applying the discounts.

        Returns:
            Dict[str, Any]: Result with final price, applied discounts, errors,
            stackable hint, suggested discounts, and attempted codes.
        """
        order = get_order_by_id(order_id)
        result: Dict[str, Any] = {
            "final_price": float(order.total_price),
            "discounts_applied": [],
            "errors": [],
            "stackable_hint": None,
            "suggested_discounts": [],
            "codes_attempted": codes,
        }

        try:
            discounts = DiscountEngine.fetch_by_codes(codes, order.website)
            applicator = DiscountEngine(order, user, discounts)

            discount_result = applicator.apply_discounts()

            result.update({
                "final_price": discount_result.get(
                    "final_price", result["final_price"]
                ),
                "discounts_applied": discount_result.get(
                    "discounts_applied", []
                ),
                "errors": discount_result.get("errors", []),
            })

            DiscountUsageTracker.track_multiple(discounts, order, user)

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
            logger.warning(
                f"Discount validation failed for order {order.id}: {ve}"
            )

            suggestions = DiscountSuggestionService.get_suggestions(
                order.website
            )
            result.update({
                "errors": [str(ve)],
                "suggested_discounts": suggestions,
            })
            return result

        except Exception as exc:
            logger.exception(
                f"Critical error applying discounts on order {order.id}: {exc}"
            )
            notify_admin_of_error(
                f"Discount error on order {order.id}: {exc}"
            )

            suggestions = DiscountSuggestionService.get_suggestions(
                order.website
            )
            result.update({
                "errors": [
                    "Unexpected internal error. Please try again later."
                ],
                "suggested_discounts": suggestions,
            })
            return result
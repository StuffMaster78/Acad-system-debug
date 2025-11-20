from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order
from activity.utils.decorators import auto_log_activity


class ApplyDirectDiscountService:
    """
    Service to apply fixed discounts to an order.

    Methods:
        apply_discount: Applies discount to order.
    """

    @auto_log_activity(
        action_type="ORDER",
        get_user=lambda a, k, r: r.client,
        get_website=lambda a, k, r: r.website,
        get_description=lambda a, k, r: (
            f"Discount of ${r.discount} applied to Order #{r.id}."
        ),
        get_metadata=lambda a, k, r: {
            "order_id": r.id,
            "discount": float(r.discount),
            "new_total": float(r.total_price),
        },
        get_triggered_by=lambda a, k, r: k.get("request").user
        if "request" in k else None
    )
    def apply_discount(
        self, order_id: int, discount_amount: float,
        *, request=None
    ) -> Order:
        """
        Apply discount to the order.

        Args:
            order_id (int): ID of the order.
            discount_amount (float): Amount to discount.
            request (HttpRequest, optional): Used to get triggered_by.

        Returns:
            Order: The order with applied discount.

        Raises:
            ValueError: If discount is invalid or order not eligible.
        """
        order = get_order_by_id(order_id)

        if order.status in (
            "completed", "unpaid", "approved", "cancelled", "archived"
        ):
            raise ValueError(
                f"Cannot apply discount to order {order_id} "
                f"in status {order.status}."
            )

        if discount_amount <= 0 or discount_amount > order.total_price:
            raise ValueError("Invalid discount amount.")

        order.discount = discount_amount
        order.total_price -= discount_amount
        save_order(order)
        return order
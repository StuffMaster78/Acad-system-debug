from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order


class ApplyDirectDiscountService:
    """
    Service to apply fixed discounts to an order.

    Methods:
        apply_discount: Applies discount to order.
    """

    def apply_discount(self, order_id: int, discount_amount: float) -> Order:
        """
        Apply discount to the order.

        Args:
            order_id (int): ID of the order.
            discount_amount (float): Amount to discount.

        Returns:
            Order: The order with applied discount.

        Raises:
            ValueError: If discount is invalid or order not eligible.
        """
        order = get_order_by_id(order_id)

        if order.status in ('completed','unpaid', 'approved', 'cancelled'):
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
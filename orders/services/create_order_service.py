from orders.models import Order
from orders.utils.order_utils import save_order


class CreateOrderService:
    """
    Service to handle the creation of new orders.

    Methods:
        create_order: Creates and saves a new order instance.
    """

    def create_order(self, user, **order_data) -> Order:
        """
        Create a new order with the provided data.

        Args:
            **order_data: Arbitrary keyword arguments for order fields.

        Returns:
            Order: The newly created order instance.
        """
        order = Order.objects.create(user=user, **order_data)
        self.order = order
        save_order(order)
        return order
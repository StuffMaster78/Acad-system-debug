from orders.models import Order
from orders.utils.order_utils import save_order
from activity.utils.decorators import auto_log_activity
from notifications_system.services.dispatcher  import notify_user

class CreateOrderService:
    """
    Service to handle the creation of new orders.

    Methods:
        create_order: Creates and saves a new order instance.
    """
    @auto_log_activity(
    action_type="ORDER",
    get_user=lambda a, k, r: r.client,
    get_website=lambda a, k, r: r.website,
    get_description=lambda a, k, r: f"Order #{r.id} created.",
    get_metadata=lambda a, k, r: {"order_id": r.id, "status": r.status}
    )
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
        notify_user(
            user=order.user,
            message="Your order has been created successfully.",
            context={"order_id": order.id, "status": order.status},
            event="order_created",
            channels=["email", "push", "websocket"],
            tenant=order.website,
            actor=user,
            template_name="order_created",
            priority=5,
            is_critical=True,
            is_digest=False,
            is_silent=False,
            email_override=None
        )
        return order
    
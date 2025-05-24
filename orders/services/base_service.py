class OrderService:
    """
    Base class for order-related services.

    Provides shared utilities and holds the order instance.
    """

    def __init__(self, order):
        """
        Initialize with an Order instance.

        Args:
            order (Order): The order instance to operate on.
        """
        self.order = order

    def save(self):
        """Save the order instance to the database."""
        self.order.save()

    def reload(self):
        """Reload the order instance from the database."""
        self.order.refresh_from_db()
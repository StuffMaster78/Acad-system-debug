class OrderApprovalService:
    """
    Handles approval logic for special orders by staff users.
    """

    @staticmethod
    def approve_special_order(order, user):
        """
        Marks the special order as approved by an admin or support user.

        Args:
            order (SpecialOrder): The order to be approved.
            user (User): The user approving the order.

        Raises:
            ValueError: If the order is not in a valid approval state.

        Returns:
            SpecialOrder: The updated approved order.
        """
        if order.status != 'awaiting_approval':
            raise ValueError("Order is not awaiting approval.")

        order.is_approved = True
        order.status = 'in_progress'
        order.approved_by = user  # Optional: track who approved it
        order.save()

        return order
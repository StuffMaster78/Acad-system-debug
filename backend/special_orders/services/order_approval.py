class OrderApprovalService:
    """
    Handles approval logic for special orders by staff users.
    """

    @staticmethod
    def approve_special_order(order, user):
        """
        Marks the special order as approved by an admin or support user.
        
        After approval, the order status transitions to 'in_progress' if deposit
        is paid, otherwise remains 'awaiting_approval' until payment is received.

        Args:
            order (SpecialOrder): The order to be approved.
            user (User): The user approving the order.

        Raises:
            ValueError: If the order is not in a valid approval state.

        Returns:
            SpecialOrder: The updated approved order.
        """
        if order.status not in ['inquiry', 'awaiting_approval']:
            raise ValueError(
                f"Order cannot be approved from status '{order.status}'. "
                "Order must be in 'inquiry' or 'awaiting_approval' status."
            )

        order.is_approved = True
        
        # Check if deposit is paid to determine next status
        # If deposit is paid (or admin marked paid), move to in_progress
        # Otherwise, keep as awaiting_approval until payment
        deposit_paid = (
            order.admin_marked_paid or
            (order.deposit_required and 
             order.installments.filter(is_paid=True).exists())
        )
        
        if deposit_paid:
            order.status = 'in_progress'
        else:
            order.status = 'awaiting_approval'
        
        order.save()

        return order
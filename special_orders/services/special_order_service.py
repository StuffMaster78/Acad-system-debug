from django.core.exceptions import ValidationError
from special_orders.models import SpecialOrder, PredefinedSpecialOrderConfig
from special_orders.services.services_orders import get_deposit_percentage


class SpecialOrderService:
    """
    Service class to manage operations related to SpecialOrder.
    """

    @staticmethod
    def create_special_order(
        client,
        website,
        order_type,
        predefined_type=None,
        duration_days=None,
        inquiry_details=''
    ):
        """
        Creates a new special order.

        Args:
            client (User): The client creating the order.
            website (Website): The website associated with the order.
            order_type (str): 'predefined' or 'estimated'.
            predefined_type (PredefinedSpecialOrderConfig, optional): Predefined config.
            duration_days (int, optional): Number of days requested.
            inquiry_details (str, optional): Custom user inquiry or description.

        Returns:
            SpecialOrder: The created special order instance.

        Raises:
            ValidationError: If pricing information is missing.
        """
        if order_type == 'predefined':
            if not predefined_type or not duration_days:
                raise ValidationError("Predefined orders require a type and duration.")

            duration_price = predefined_type.durations.filter(
                duration_days=duration_days
            ).first()

            if not duration_price:
                raise ValidationError("No pricing found for the selected duration.")

            total_cost = duration_price.price

        elif order_type == 'estimated':
            # For estimated orders, assume cost is determined later or handled separately.
            total_cost = 0
        else:
            raise ValidationError("Invalid order type.")

        # For predefined orders, deposit equals total_cost (handled in save method)
        # For estimated orders, deposit will be calculated in save method based on settings
        deposit_amount = None
        if order_type == 'predefined':
            deposit_amount = total_cost  # Full payment for predefined
        elif order_type == 'estimated':
            # Deposit will be calculated in save() method when total_cost is set
            deposit_amount = 0

        special_order = SpecialOrder.objects.create(
            client=client,
            website=website,
            order_type=order_type,
            predefined_type=predefined_type,
            duration_days=duration_days,
            total_cost=total_cost if order_type == 'predefined' else 0,
            deposit_required=deposit_amount if order_type == 'predefined' else None,
            inquiry_details=inquiry_details
        )

        return special_order
    
    # @staticmethod
    # def approve_special_order(order: SpecialOrder) -> SpecialOrder:
    #     """
    #     Approves the given special order.

    #     Args:
    #         order (SpecialOrder): The order to approve.

    #     Returns:
    #         SpecialOrder: The approved order.
    #     """
    #     if order.is_approved:
    #         raise ValidationError("Order is already approved.")

    #     order.is_approved = True
    #     order.status = 'approved'  # Replace with enum or constant if you have one
    #     order.save()
    #     return order

    @staticmethod
    def update_special_order(order, is_approved=None, status=None):
        """
        Updates an existing special order.

        Args:
            order (SpecialOrder): The order to update.
            is_approved (bool, optional): Approval status.
            status (str, optional): New status value.

        Returns:
            SpecialOrder: The updated order.
        """
        if is_approved is not None:
            order.is_approved = is_approved
        if status:
            order.status = status
        order.save()
        return order

    @staticmethod
    def validate_special_order(order):
        """
        Validates an existing special order's integrity.

        Args:
            order (SpecialOrder): The special order instance.

        Raises:
            ValidationError: If the order is misconfigured.
        """
        if order.order_type == 'predefined' and not order.predefined_type:
            raise ValidationError("Predefined order type is required.")
        if order.total_cost <= 0:
            raise ValidationError("Total cost must be greater than zero.")
        
    @staticmethod
    def override_payment(order: SpecialOrder, new_total_cost: float) -> SpecialOrder:
        """
        Overrides the payment amount for a special order.

        Args:
            order (SpecialOrder): The special order to modify.
            new_total_cost (float): The new total cost to apply.

        Returns:
            SpecialOrder: The updated special order.

        Raises:
            ValidationError: If the new total cost is not valid.
        """
        if new_total_cost <= 0:
            raise ValidationError("New total cost must be greater than zero.")

        order.total_cost = new_total_cost
        order.deposit_required = new_total_cost * 0.5  # You can refactor to fetch deposit %
        order.save()
        return order

    @staticmethod
    def complete_special_order(order: SpecialOrder) -> SpecialOrder:
        """
        Marks a special order as complete.

        Args:
            order (SpecialOrder): The special order to complete.

        Returns:
            SpecialOrder: The completed special order.

        Raises:
            ValidationError: If the order is not in an approvable or completable state.
        """
        if not order.is_approved:
            raise ValidationError("Cannot complete an unapproved order.")

        if order.status == 'completed':
            raise ValidationError("Order is already completed.")

        order.status = 'completed'  # Replace with Enum/Constant if you're fancy
        order.save()
        return order
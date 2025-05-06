from django.core.exceptions import ValidationError
from .models import SpecialOrder, PredefinedSpecialOrderConfig
from special_orders.services.services_orders import get_deposit_percentage

class SpecialOrderService:
    """
    Service class to manage operations related to SpecialOrder.
    """

    @staticmethod
    def create_special_order(client, website, order_type, predefined_type, 
                             duration_days, website, inquiry_details=''):
        """
        Creates a new special order.

        Args:
            client (User): The client creating the order.
            order_type (str): The type of the order (predefined or estimated).
            predefined_type (PredefinedSpecialOrderConfig): The predefined 
                order type (if applicable).
            duration_days (int): The number of days for the special order.
            website (Website): The website associated with the order.
            inquiry_details (str, optional): Additional details about the order.

        Returns:
            SpecialOrder: The created special order object.
        """
        deposit_percentage = get_deposit_percentage(website)

        # Calculate the deposit amount based on the total order cost
        deposit_amount = order_details['total_cost'] * (deposit_percentage / 100)

        special_order = SpecialOrder.objects.create(
            website=website,
            client=client,
            order_type=order_type,
            predefined_type=predefined_type,
            duration_days=duration_days,
            total_cost=order_details['total_cost'],
            deposit_required=deposit_amount,
            inquiry_details=inquiry_details
        )
        
        # Apply pricing for predefined orders
        if order_type == 'predefined' and predefined_type:
            duration_price = predefined_type.durations.filter(
                duration_days=duration_days
            ).first()
            if duration_price:
                special_order.total_cost = duration_price.price
                special_order.save()
        
        return special_order

    @staticmethod
    def update_special_order(order, is_approved=None, status=None):
        """
        Updates an existing special order.

        Args:
            order (SpecialOrder): The order to update.
            is_approved (bool, optional): Whether the order is approved.
            status (str, optional): The updated status of the order.

        Returns:
            SpecialOrder: The updated special order object.
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
        Validates a special order.

        Args:
            order (SpecialOrder): The special order to validate.

        Raises:
            ValidationError: If the order is invalid.
        """
        if order.order_type == 'predefined' and not order.predefined_type:
            raise ValidationError("Predefined order type is required.")
        if order.total_cost <= 0:
            raise ValidationError("Total cost must be greater than zero.")
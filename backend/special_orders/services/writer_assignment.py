"""
Handles logic for assigning writers to special orders.
"""
from decimal import Decimal

def assign_writer(order, writer, payment_amount=None, payment_percentage=None):
    """
    Assigns a writer to a special order with optional payment amount or percentage.

    Args:
        order (SpecialOrder): The special order to which the writer is being assigned.
        writer (User): The writer being assigned to the order.
        payment_amount (Decimal, optional): Fixed payment amount set by admin.
        payment_percentage (Decimal, optional): Payment percentage of order total set by admin.

    Raises:
        ValueError: If the assigned user is not a writer, or if both amount and percentage are provided.
    """
    if writer.role != 'writer':
        raise ValueError("Assigned user must be a writer.")
    
    if payment_amount and payment_percentage:
        raise ValueError("Cannot set both payment_amount and payment_percentage. Choose one.")

    order.writer = writer
    
    # Set payment amount or percentage if provided
    if payment_amount is not None:
        order.writer_payment_amount = Decimal(str(payment_amount))
        order.writer_payment_percentage = None  # Clear percentage if amount is set
    elif payment_percentage is not None:
        order.writer_payment_percentage = Decimal(str(payment_percentage))
        order.writer_payment_amount = None  # Clear amount if percentage is set
    
    order.save()
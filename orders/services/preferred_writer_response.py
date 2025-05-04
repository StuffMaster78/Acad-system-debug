from django.utils import timezone
from orders.models import Order, PreferredWriterResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

def respond_to_preferred_order(writer, order_id, response, reason=None):
    """
    Allows a preferred writer to respond to an order request (accept/decline).

    Args:
        writer (User): The writer responding to the order.
        order_id (int): The ID of the order.
        response (str): The writer's response, either 'accepted' or 'declined'.
        reason (str, optional): The reason for declining the order (if any).

    Returns:
        Order: The updated order after the writer's response.
    
    Raises:
        ObjectDoesNotExist: If the order does not exist or is not assigned to the writer.
    """
    try:
        order = Order.objects.get(id=order_id)

        if order.preferred_writer != writer:
            raise ObjectDoesNotExist(f"Order #{order.id} is not assigned to this writer.")
        
        # Start a transaction to handle changes atomically
        with transaction.atomic():
            # Log the writer's response
            response_record = PreferredWriterResponse.objects.create(
                order=order,
                writer=writer,
                response=response,
                reason=reason if response == 'declined' else None
            )

            # Handle the order's status based on the writer's response
            if response == 'accepted':
                order.status = 'in_progress'
            else:  # response == 'declined'
                order.status = 'available'  # It goes back to the pool

            order.save()

            return order
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(f"Order #{order_id} does not exist or no preferred writer.")
"""
Handles logic for assigning writers to special orders.
"""

def assign_writer(order, writer):
    """
    Assigns a writer to a special order.

    Args:
        order (SpecialOrder): The special order to which the writer is being assigned.
        writer (User): The writer being assigned to the order.

    Raises:
        ValueError: If the assigned user is not a writer.
    """
    if writer.role != 'writer':
        raise ValueError("Assigned user must be a writer.")

    order.writer = writer
    order.save()
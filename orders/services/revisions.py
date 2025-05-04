from datetime import timedelta
from django.utils import timezone
from orders.models import Order
from .utils import get_order_config


def get_revision_deadline():
    """
    Get the maximum number of days after which revisions are no longer allowed.
    Fetches this configuration from the order settings.
    """
    order_config = get_order_config()
    return timedelta(days=order_config.revision_deadline_days)


def is_within_revision_period(order):
    """
    Check if the order is within the allowed revision period.
    Revisions are only allowed if the order was completed within the configured time limit.
    
    Args:
        order (Order): The order to check.
        
    Returns:
        bool: True if revision is within the allowed period, False otherwise.
    """
    revision_deadline = get_revision_deadline()
    time_elapsed = timezone.now() - order.completed_at

    return time_elapsed <= revision_deadline


def can_request_revision(order, request_user):
    """
    Check whether the order is eligible for a revision request.
    This checks if the order is in 'Completed'
    state and is within the revision period.
    
    Args:
        order (Order): The order to check.
        
    Returns:
        bool: True if the revision can be requested, False otherwise.
    """
    # Check if the order is eligible for a revision based on the policy
    if order.client != request_user:
        raise PermissionDenied("Only the client can request revisions.")
    
    # Get the revision policy for the website
    policy = order.website.revision_policies.filter(active=True).first()

    if not policy:
        raise PolicyNotFound("No active revision policy found for this website.")

    # Check if the revision request is within the free revision window
    if (timezone.now() - order.created_at).days <= policy.max_revision_days:
        return True
    
    # Handle post-free revision (you might add extra charge logic here)
    return False


def request_revision(order, reason):
    """
    Handle the revision request for a given order.
    
    Args:
        order (Order): The order to revise.
        reason (str): The reason the client is requesting the revision.
        
    Returns:
        bool: True if revision was successfully requested, False otherwise.
    """
    if not can_request_revision(order):
        return False  # Not eligible for revision

    # Log the revision request (e.g., adding it to a revision history or something similar)
    order.revision_request = reason
    order.status = 'in_revision'
    order.save()

    return True


def process_revision(order, revised_work):
    """
    Process the revision of an order by the writer.
    This function moves the order back to 'Completed' once
    the writer submits the revision.
    
    Args:
        order (Order): The order being revised.
        revised_work (str): The revised work content provided by the writer.
        
    Returns:
        bool: True if the revision was successfully processed, False otherwise.
    """
    if order.status != 'in_revision':
        return False  # Order is not in revision state, cannot process

    order.revised_work = revised_work
    order.status = 'completed'
    order.save()

    return True


def deny_revision(order, reason):
    """
    Deny the revision request for an order. This might
    occur if the revision period has expired
    or if the revision is deemed unnecessary.
    
    Args:
        order (Order): The order for which the revision is denied.
        reason (str): The reason for denying the revision.
        
    Returns:
        bool: True if the revision was denied, False otherwise.
    """
    if order.status != 'completed':
        return False  # Order is not in a state that can have a revision denied

    order.revision_request_denied_reason = reason
    order.status = 'revision_denied'
    order.save()

    return True
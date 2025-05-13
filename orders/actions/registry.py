import logging
from enum import Enum
from .base import OrderActionRegistry

logger = logging.getLogger(__name__)
class OrderStatus(Enum):
    """
    Enum representing different statuses an order can have.
    """
    CREATED = 'created'
    UNPAID = 'unpaid'
    PENDING = 'pending'
    ON_HOLD = 'on_hold'
    AVAILABLE = 'available'
    PENDING_PREFERRED = 'pending_preferred'
    CRITICAL = 'critical'
    ASSIGNED = 'assigned'
    LATE = 'late'
    REVISION = 'revision'
    DISPUTED = 'disputed'
    COMPLETED = 'completed'
    APPROVED = 'approved'
    CANCELLED = 'cancelled'
    ARCHIVED = 'archived'
    EXPIRED = 'expired'
    UNDER_REVIEW = 'under_review'
    REOPENED = 're_opened'
    RATED = 'rated'
    REVIEWED = 'reviewed'

class OrderActionNames(Enum):
    """
    Enum for action names associated with order status transitions.
    """
    TRANSITION_TO_PENDING = "transition_to_pending"
    PUT_ON_HOLD = "put_on_hold"
    RESUME_ORDER = "resume_order"
    ASSIGN_WRITER = "assign_writer"
    COMPLETE_ORDER = "complete_order"
    DISPUTE_ORDER = "dispute_order"
    APPROVE_ORDER = "approve_order"
    CANCEL_ORDER = "cancel_order"
    ARCHIVE_ORDER = "archive_order"
    LATE_ORDER = "late_order"
    REVISION_ORDER = "revision_order"
    REQUEST_REVISION = "request_revision"
    PROCESS_REVISION = "process_revision"
    DENY_REVISION = "deny_revision"
    REASSIGN_ORDER = "reassign_order"

# Registering all actions in the registry for all states
def register_actions():
    """
    Registers all the order actions into the action registry using their
    respective action names.
    """
    actions = {
        OrderStatus.CREATED: [
            OrderActionNames.TRANSITION_TO_PENDING, OrderActionNames.PUT_ON_HOLD
        ],
        OrderStatus.UNPAID: [
            OrderActionNames.TRANSITION_TO_PENDING, OrderActionNames.CANCEL_ORDER
        ],
        OrderStatus.PENDING: [
            OrderActionNames.RESUME_ORDER, OrderActionNames.CANCEL_ORDER,
            OrderActionNames.PUT_ON_HOLD
        ],
        OrderStatus.ON_HOLD: [
            OrderActionNames.RESUME_ORDER, OrderActionNames.CANCEL_ORDER
        ],
        OrderStatus.AVAILABLE: [
            OrderActionNames.ASSIGN_WRITER, OrderActionNames.COMPLETE_ORDER
        ],
        OrderStatus.PENDING_PREFERRED: [
            OrderActionNames.RESUME_ORDER, OrderActionNames.CANCEL_ORDER
        ],
        OrderStatus.CRITICAL: [
            OrderActionNames.RESUME_ORDER, OrderActionNames.CANCEL_ORDER
        ],
        OrderStatus.ASSIGNED: [
            OrderActionNames.COMPLETE_ORDER, OrderActionNames.REQUEST_REVISION
        ],
        OrderStatus.LATE: [
            OrderActionNames.COMPLETE_ORDER, OrderActionNames.REVISION_ORDER
        ],
        OrderStatus.REVISION: [
            OrderActionNames.REQUEST_REVISION, OrderActionNames.PROCESS_REVISION,
            OrderActionNames.DENY_REVISION
        ],
        OrderStatus.DISPUTED: [
            OrderActionNames.REQUEST_REVISION, OrderActionNames.APPROVE_ORDER
        ],
        OrderStatus.COMPLETED: [
            OrderActionNames.ARCHIVE_ORDER
        ],
        OrderStatus.APPROVED: [
            OrderActionNames.ARCHIVE_ORDER
        ],
        OrderStatus.CANCELLED: [
            OrderActionNames.ARCHIVE_ORDER
        ],
        OrderStatus.ARCHIVED: [],
        OrderStatus.EXPIRED: [
            OrderActionNames.ARCHIVE_ORDER
        ],
        OrderStatus.UNDER_REVIEW: [
            OrderActionNames.APPROVE_ORDER, OrderActionNames.DENY_REVISION
        ],
        OrderStatus.REOPENED: [
            OrderActionNames.RESUME_ORDER
        ],
        OrderStatus.RATED: [
            OrderActionNames.APPROVE_ORDER, OrderActionNames.ARCHIVE_ORDER
        ],
        OrderStatus.REVIEWED: [
            OrderActionNames.ARCHIVE_ORDER
        ],
        OrderStatus.REASSIGN: [
            OrderActionNames.REASSIGN_ORDER
        ],
    }

    for status, action_names in actions.items():
        for action_name in action_names:
            try:
                handler_class = globals().get(action_name.value)
                if handler_class:
                    OrderActionRegistry.register(action_name.value, handler_class)
            except Exception as e:
                logger.error(f"Failed to register action {action_name.value} "
                             f"for status {status.value}: {e}")

# Optionally, you could also expose a function to list all available actions
def get_all_actions():
    """
    Retrieve all registered actions in the order action registry.
    :return: A dictionary of action names and their corresponding handler
             classes.
    """
    return OrderActionRegistry.get_registry()
from enum import Enum


class OrderStatus(str, Enum):
    """Represents the possible states of an order."""
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    IN_REVIEW = 'in_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    IN_PROGRESS = 'in_progress'
    REVISION_REQUESTED = 'revision_requested'
    ON_REVISION = 'on_revision'
    REVISED = 'revised'
    COMPLETED = 'completed'

    RATED = 'rated'
    REVIEWED = 'reviewed'
    CLOSED = 'closed'

    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

    # Extra system/admin/internal statuses
    CREATED = 'created'
    REASSIGNED = 'reassigned'
    UNPAID = 'unpaid'
    PENDING = 'pending'
    ON_HOLD = 'on_hold'
    AVAILABLE = 'available'
    PENDING_PREFERRED = 'pending_preferred'
    CRITICAL = 'critical'
    ASSIGNED = 'assigned'
    LATE = 'late'
    DISPUTED = 'disputed'
    ARCHIVED = 'archived'
    EXPIRED = 'expired'
    UNDER_REVIEW = 'under_review'
    REOPENED = 're_opened'


# Order transitions allowed from each state
ALLOWED_TRANSITIONS = {
    OrderStatus.DRAFT: [OrderStatus.SUBMITTED, OrderStatus.CANCELLED],
    OrderStatus.SUBMITTED: [OrderStatus.IN_REVIEW, OrderStatus.CANCELLED],
    OrderStatus.IN_REVIEW: [
        OrderStatus.APPROVED,
        OrderStatus.REJECTED,
        OrderStatus.CANCELLED,
    ],
    OrderStatus.APPROVED: [OrderStatus.IN_PROGRESS],
    OrderStatus.REJECTED: [OrderStatus.REFUNDED],

    OrderStatus.IN_PROGRESS: [
        OrderStatus.COMPLETED,
        OrderStatus.REVISION_REQUESTED,
        OrderStatus.CANCELLED,
    ],
    OrderStatus.REVISION_REQUESTED: [OrderStatus.ON_REVISION],
    OrderStatus.ON_REVISION: [OrderStatus.REVISED],
    OrderStatus.REVISED: [
        OrderStatus.IN_PROGRESS,
        OrderStatus.REVISION_REQUESTED,
    ],
    OrderStatus.COMPLETED: [OrderStatus.APPROVED],
    OrderStatus.APPROVED: [OrderStatus.RATED],
    OrderStatus.RATED: [OrderStatus.REVIEWED],
    OrderStatus.REVIEWED: [OrderStatus.CLOSED],

    OrderStatus.CANCELLED: [OrderStatus.REFUNDED],
    OrderStatus.REFUNDED: [OrderStatus.CLOSED],
    OrderStatus.CLOSED: [],
}


# Role-based permissions for performing status transitions
ROLE_TRANSITION_PERMISSIONS = {
    "superadmin": list(OrderStatus),
    "admin": [
        OrderStatus.SUBMITTED,
        OrderStatus.IN_REVIEW,
        OrderStatus.APPROVED,
        OrderStatus.REJECTED,
        OrderStatus.IN_PROGRESS,
        OrderStatus.COMPLETED,
        OrderStatus.REVISION_REQUESTED,
        OrderStatus.ON_REVISION,
        OrderStatus.REVISED,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED,
        OrderStatus.CLOSED,
    ],
    "support": [
        OrderStatus.SUBMITTED,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED,
        OrderStatus.CLOSED,
    ],
    "editor": [
        OrderStatus.APPROVED,
        OrderStatus.IN_PROGRESS,
        OrderStatus.REVISION_REQUESTED,
        OrderStatus.ON_REVISION,
        OrderStatus.REVISED,
        OrderStatus.COMPLETED,
    ],
    "writer": [
        OrderStatus.IN_PROGRESS,
        OrderStatus.REVISION_REQUESTED,
        OrderStatus.ON_REVISION,
        OrderStatus.REVISED,
        OrderStatus.COMPLETED,
    ],
    "client": [
        OrderStatus.APPROVED,
        OrderStatus.RATED,
        OrderStatus.REVIEWED,
    ],
}


@classmethod
def choices(cls):
        """
        Returns a list of tuples (value, label) for each status in the enum.
        """
        return [
            (status.value, status.name.replace('_', ' ').title()) 
            for status in cls
        ]
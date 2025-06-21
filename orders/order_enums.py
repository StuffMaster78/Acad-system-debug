from enum import Enum
from django.db import models

class OrderFlags(str, Enum):
    """
    Enum representing different flags that can be applied to an order.
    """
    URGENT_ORDER = 'UO'
    FIRST_CLIENT_ORDER = 'FCO'
    HIGH_VALUE_ORDER = 'HVO'
    PREFERRED_ORDER = 'PO'
    RETURNING_CLIENT_ORDER = 'RCO'
    CRITICAL_ORDER = 'CO'
    lATE_ORDER = 'LO'
    DISPUTED_ORDER = 'DO'
    ARCHIVED_ORDER = 'AO'
    EXPIRED_ORDER = 'EO'
    UNDER_REVIEW_ORDER = 'URO'
    REOPENED_ORDER = 'RO'
    
    @classmethod
    def choices(cls):
        """
        Returns a list of tuples (value, label) for each flag in the enum.
        """
        return [
            (flag.value, flag.name.replace('_', ' ').title()) 
            for flag in cls
        ]
    
class OrderPaymentStatus(str, Enum):
    """
    Enum representing the payment status of an order.
    UNPAID: Order is created but not yet paid for.

    PAID: Payment complete.

    PARTIALLY_PAID: Partial payment received.

    REFUNDED: Refunded fully or partially.

    CHARGEBACK: Payment was forcibly reversed.

    FAILED: Attempted payment failed.

    PENDING: Waiting for payment confirmation (e.g., crypto, bank transfer).

    CANCELLED: Cancelled before/during payment.
    """

    UNPAID = "unpaid"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    REFUNDED = "refunded"
    CHARGEBACK = "chargeback"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    
class DisputeStatusEnum(Enum):
    """
    Enum representing the different statuses a dispute can have.
    """
    OPEN = 'open'
    IN_REVIEW = 'in_review'
    RESOLVED = 'resolved'
    ESCALATED = 'escalated'
    CLOSED = 'closed'

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples (value, label) for each dispute status.
        """
        return [
            (status.value, status.name.replace('_', ' ').title()) 
            for status in cls
        ]


class ResolutionOutcome(Enum):
    """
    Enum representing the different outcomes of a dispute.
    """
    WRITER_WINS = "writer_wins"
    CLIENT_WINS = "client_wins"
    EXTEND_DEADLINE = "extend_deadline"
    REASSIGN = "reassign"
class SpacingOptions(Enum):
    """
    Enum representing the different spacing options for an order.
    """
    SINGLE = 'single'
    DOUBLE = 'double'

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples (value, label) for each spacing type in the enum.
        """
        return [
            (spacing.value, spacing.name.capitalize()) 
            for spacing in cls
        ]

class WriterPaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
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

    UNDER_EDITING = "under_editing"

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



class OrderRequestStatus(models.TextChoices):
    """ 
    Represents the status of an order request made by a writer.
    """
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"
    EXPIRED = "expired", "Expired"

# class OrderRequestType(models.TextChoices):
#     """
#     Represents the type of order request made by a writer.
#     """
#     WRITER_REQUEST = "writer_request", "Writer Request"
#     ORDER_REQUEST = "order_request", "Order Request"

#     @classmethod
#     def choices(cls):
#         """
#         Returns a list of tuples (value, label) for each type in the enum.
#         """
#         return [
#             (request_type.value, request_type.label) 
#             for request_type in cls
#         ]

class WebhookEvent(models.TextChoices):
    """Webhook events for order updates."""
    ORDER_CREATED = "order_created", "Order Created"
    ORDER_ASSIGNED = "order_assigned", "Order Assigned"
    ORDER_REVISED = "order_revised", "Order Revised"
    ORDER_SUBMITTED = "order_submitted", "Order Submitted"
    ORDER_REOPENED = "order_reopened", "Order Reopened"
    ORDER_ON_HOLD = "order_on_hold", "Order On Hold"
    ORDER_CANCELLED = "order_cancelled", "Order Cancelled"
    ORDER_ON_REVISION = "order_on_revision", "Order On Revision"
    REVISION_REQUESTED = "revision_requested", "Revision Requested"
    ORDER_DISPUTED = "order_disputed", "Order Disputed"
    ORDER_COMPLETED = "order_completed", "Order Completed"
    ORDER_REVIEWED = "order_reviewed", "Order Reviewed"
    ORDER_RATED = "order_rated", "Order Rated"
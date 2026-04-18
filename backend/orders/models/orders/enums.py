from __future__ import annotations

from django.db import models


class OrderStatus(models.TextChoices):
    """
    Represent the main order lifecycle states.

    These states describe the broad lifecycle of the order itself.
    They do not try to encode every staffing, revision, adjustment, or
    deletion subworkflow.
    """

    CREATED = "created", "Created"
    UNPAID = "unpaid", "Unpaid"
    READY_FOR_STAFFING = (
        "ready_for_staffing",
        "Ready for Staffing",
    )
    PAID = "paid", "Paid"
    IN_PROGRESS = "in_progress", "In Progress"
    ON_HOLD = "on_hold", "On Hold"
    DISPUTED = "disputed", "Disputed"
    SUBMITTED = "submitted", "Submitted"
    COMPLETED = "completed", "Completed"
    QA_REVIEW = "qa_review", "QA Review"
    CANCELLED = "cancelled", "Cancelled"
    ARCHIVED = "archived", "Archived"



class OrderVisibilityMode(models.TextChoices):
    """
    Represent how a paid order is exposed to writers.
    """

    HIDDEN = "hidden", "Hidden"
    POOL = "pool", "Pool"
    PREFERRED_WRITER_ONLY = (
        "preferred_writer_only",
        "Preferred Writer Only",
    )


class PreferredWriterStatus(models.TextChoices):
    """
    Represent preferred writer routing state.
    """

    NOT_REQUESTED = "not_requested", "Not Requested"
    INVITED = "invited", "Invited"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
    EXPIRED = "expired", "Expired"
    FALLBACK_TO_POOL = "fallback_to_pool", "Fallback To Pool"


class OrderInterestType(models.TextChoices):
    """
    Represent the type of staffing intent a writer can submit.
    """

    BID = "bid", "Bid"
    SHOW_INTEREST = "show_interest", "Show Interest"
    REQUEST_TAKE = "request_take", "Request Take"
    PREFERRED_WRITER_INVITATION = (
        "preferred_writer_invitation",
        "Preferred Writer Invitation",
    )


class OrderInterestStatus(models.TextChoices):
    """
    Represent the lifecycle of a writer interest record.
    """

    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"
    DECLINED = "declined", "Declined"
    EXPIRED = "expired", "Expired"
    SUPERSEDED = "superseded", "Superseded"


class OrderAssignmentSource(models.TextChoices):
    """
    Represent how the current assignment came to exist.
    """

    STAFF_ASSIGNMENT = "staff_assignment", "Staff Assignment"
    AUTO_ASSIGNMENT = "auto_assignment", "Auto Assignment"
    SELF_TAKE = "self_take", "Self Take"
    ACCEPTED_INTEREST = "accepted_interest", "Accepted Interest"
    PREFERRED_WRITER_ACCEPTANCE = (
        "preferred_writer_acceptance",
        "Preferred Writer Acceptance",
    )
    REASSIGNMENT = "reassignment", "Reassignment"


class OrderAssignmentStatus(models.TextChoices):
    """
    Represent assignment lifecycle states.
    """

    ACTIVE = "active", "Active"
    RELEASED = "released", "Released"
    REASSIGNED = "reassigned", "Reassigned"
    DROPPED = "dropped", "Dropped"
    CANCELLED = "cancelled", "Cancelled"


class OrderHoldStatus(models.TextChoices):
    """
    Represent hold lifecycle states.
    """

    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    RELEASED = "released", "Released"
    CANCELLED = "cancelled", "Cancelled"


class OrderTimelineEventType(models.TextChoices):
    """
    Represent order timeline event types.
    """

    CREATED = "created", "Created"
    PAID = "paid", "Paid"
    POOL_OPENED = "pool_opened", "Pool Opened"
    PREFERRED_WRITER_INVITED = (
        "preferred_writer_invited",
        "Preferred Writer Invited",
    )
    PREFERRED_WRITER_DECLINED = (
        "preferred_writer_declined",
        "Preferred Writer Declined",
    )
    INTEREST_CREATED = "interest_created", "Interest Created"
    ASSIGNED = "assigned", "Assigned"
    REASSIGNED = "reassigned", "Reassigned"
    HOLD_REQUESTED = "hold_requested", "Hold Requested"
    HOLD_ACTIVATED = "hold_activated", "Hold Activated"
    HOLD_RELEASED = "hold_released", "Hold Released"
    SUBMITTED = "submitted", "Submitted"
    COMPLETED = "completed", "Completed"
    REOPENED = "reopened", "Reopened"
    DISPUTED = "disputed", "Disputed"
    CANCELLED = "cancelled", "Cancelled"
    SOFT_DELETED = "soft_deleted", "Soft Deleted"
    RESTORED = "restored", "Restored"
    ADJUSTMENT_CREATED = "adjustment_created", "Adjustment Created"
    ADJUSTMENT_FUNDED = "adjustment_funded", "Adjustment Funded"
    INTEREST_WITHDRAWN = "interest_withdrawn", "Interest Withdrawn"
    PREFERRED_WRITER_ACCEPTED = (
        "preferred_writer_accepted",
        "Preferred Writer Accepted",
    )
    PREFERRED_WRITER_EXPIRED = (
        "preferred_writer_expired",
        "Preferred Writer Expired",
    )
    RETURNED_TO_POOL = "returned_to_pool", "Returned To Pool"
    REASSIGNMENT_REQUESTED = (
    "reassignment_requested",
    "Reassignment Requested",
    )
    REASSIGNMENT_REJECTED = (
        "reassignment_rejected",
        "Reassignment Rejected",
    )
    REASSIGNMENT_CANCELLED = (
        "reassignment_cancelled",
        "Reassignment Cancelled",
    )
    ARCHIVED = "archived", "Archived"
    WRITER_ACKNOWLEDGED = (
        "writer_acknowledged",
        "Writer Acknowledged",
    )
    APPROVED = (
        "approved",
        "Approved",
    )
class OrderRevisionStatus(models.TextChoices):
    """
    Represent free revision lifecycle states.
    """

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class OrderRevisionEventType(models.TextChoices):
    """
    Represent free revision timeline event types.
    """

    CREATED = "created", "Created"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    STARTED = "started", "Started"
    SUBMITTED = "submitted", "Submitted"
    ACCEPTED = "accepted", "Accepted"
    CANCELLED = "cancelled", "Cancelled"


class OrderAdjustmentType(models.TextChoices):
    """
    Represent commercial adjustment categories.
    """

    PAGE_INCREASE = "page_increase", "Page Increase"
    SLIDE_INCREASE = "slide_increase", "Slide Increase"
    DEADLINE_DECREASE = "deadline_decrease", "Deadline Decrease"
    EXTRA_SERVICE = "extra_service", "Extra Service"
    PAID_REVISION = "paid_revision", "Paid Revision"
    SCOPE_EXPANSION = "scope_expansion", "Scope Expansion"
    OTHER = "other", "Other"


class OrderAdjustmentStatus(models.TextChoices):
    """
    Represent adjustment request lifecycle states.
    """

    PENDING_CLIENT_RESPONSE = (
        "pending_client_response",
        "Pending Client Response",
    )
    CLIENT_COUNTERED = "client_countered", "Client Countered"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
    CANCELLED = "cancelled", "Cancelled"
    FUNDING_PENDING = "funding_pending", "Funding Pending"
    FUNDED = "funded", "Funded"
    EXPIRED = "expired", "Expired"
    REVERSED = "reversed", "Reversed"


class OrderAdjustmentProposalType(models.TextChoices):
    """
    Represent adjustment proposal types.
    """

    SYSTEM_QUOTE = "system_quote", "System Quote"
    CLIENT_COUNTER = "client_counter", "Client Counter"
    STAFF_OVERRIDE = "staff_override", "Staff Override"
    FINAL_AGREEMENT = "final_agreement", "Final Agreement"


class OrderAdjustmentProposalRole(models.TextChoices):
    """
    Represent proposal actor roles.
    """

    SYSTEM = "system", "System"
    CLIENT = "client", "Client"
    WRITER = "writer", "Writer"
    STAFF = "staff", "Staff"


class OrderAdjustmentEventType(models.TextChoices):
    """
    Represent adjustment event types.
    """

    REQUEST_CREATED = "request_created", "Request Created"
    PROPOSAL_CREATED = "proposal_created", "Proposal Created"
    CLIENT_NOTIFIED = "client_notified", "Client Notified"
    CLIENT_COUNTERED = "client_countered", "Client Countered"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
    BILLING_CREATED = "billing_created", "Billing Created"
    PAYMENT_INTENT_CREATED = (
        "payment_intent_created",
        "Payment Intent Created",
    )
    PAYMENT_PARTIALLY_APPLIED = (
        "payment_partially_applied",
        "Payment Partially Applied",
    )
    PAYMENT_FULLY_APPLIED = (
        "payment_fully_applied",
        "Payment Fully Applied",
    )
    FUNDED = "funded", "Funded"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"
    REVERSED = "reversed", "Reversed"
    COMPENSATION_CREATED = (
        "compensation_created",
        "Compensation Created",
    )
    COMPENSATION_REVERSED = (
        "compensation_reversed",
        "Compensation Reversed",
    )


class OrderAdjustmentFundingStatus(models.TextChoices):
    """
    Represent adjustment funding states.
    """

    NOT_STARTED = "not_started", "Not Started"
    PAYMENT_REQUEST_CREATED = (
        "payment_request_created",
        "Payment Request Created",
    )
    PAYMENT_INTENT_CREATED = (
        "payment_intent_created",
        "Payment Intent Created",
    )
    PARTIALLY_FUNDED = "partially_funded", "Partially Funded"
    FUNDED = "funded", "Funded"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"
    REVERSED = "reversed", "Reversed"


class OrderCompensationAdjustmentStatus(models.TextChoices):
    """
    Represent writer compensation adjustment states.
    """

    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    RECOGNIZED = "recognized", "Recognized"
    REVERSED = "reversed", "Reversed"
    CANCELLED = "cancelled", "Cancelled"


class OrderCompensationAdjustmentType(models.TextChoices):
    """
    Represent writer compensation adjustment types.
    """

    PAGE_DELTA = "page_delta", "Page Delta"
    SLIDE_DELTA = "slide_delta", "Slide Delta"
    EXTRA_SERVICE = "extra_service", "Extra Service"
    DEADLINE_DELTA = "deadline_delta", "Deadline Delta"
    PAID_REVISION = "paid_revision", "Paid Revision"
    OTHER = "other", "Other"
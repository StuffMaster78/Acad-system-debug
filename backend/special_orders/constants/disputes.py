from __future__ import annotations


class DisputeStatus:
    """
    Lifecycle for special order disputes.
    """

    OPEN = "open"
    UNDER_REVIEW = "under_review"
    AWAITING_CLIENT_RESPONSE = "awaiting_client_response"
    AWAITING_STAFF_RESPONSE = "awaiting_staff_response"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

    CHOICES = [
        (OPEN, "Open"),
        (UNDER_REVIEW, "Under review"),
        (AWAITING_CLIENT_RESPONSE, "Awaiting client response"),
        (AWAITING_STAFF_RESPONSE, "Awaiting staff response"),
        (RESOLVED, "Resolved"),
        (REJECTED, "Rejected"),
        (CANCELLED, "Cancelled"),
    ]


class DisputeResolutionType:
    """
    Final outcome of a dispute.
    """

    NO_ACTION = "no_action"
    REVISION = "revision"
    PARTIAL_REFUND = "partial_refund"
    FULL_REFUND = "full_refund"
    STORE_CREDIT = "store_credit"
    MANUAL_ADJUSTMENT = "manual_adjustment"

    CHOICES = [
        (NO_ACTION, "No action"),
        (REVISION, "Revision"),
        (PARTIAL_REFUND, "Partial refund"),
        (FULL_REFUND, "Full refund"),
        (STORE_CREDIT, "Store credit"),
        (MANUAL_ADJUSTMENT, "Manual adjustment"),
    ]
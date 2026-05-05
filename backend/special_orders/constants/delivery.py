from __future__ import annotations


class DeliveryCheckpointType:
    """
    Funding or review gate before a special order action.
    """

    BEFORE_STAFFING = "before_staffing"
    BEFORE_DRAFT = "before_draft"
    BEFORE_FINAL_DELIVERY = "before_final_delivery"
    BEFORE_COMPLETION = "before_completion"

    CHOICES = [
        (BEFORE_STAFFING, "Before staffing"),
        (BEFORE_DRAFT, "Before draft"),
        (BEFORE_FINAL_DELIVERY, "Before final delivery"),
        (BEFORE_COMPLETION, "Before completion"),
    ]


class DeliveryCheckpointStatus:
    """
    Status of a delivery checkpoint.
    """

    BLOCKED = "blocked"
    UNLOCKED = "unlocked"
    WAIVED = "waived"

    CHOICES = [
        (BLOCKED, "Blocked"),
        (UNLOCKED, "Unlocked"),
        (WAIVED, "Waived"),
    ]


class SpecialOrderDeliverableStatus:
    """
    Status of a special order deliverable.
    """

    PENDING = "pending"
    UPLOADED = "uploaded"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELIVERED = "delivered"

    CHOICES = [
        (PENDING, "Pending"),
        (UPLOADED, "Uploaded"),
        (UNDER_REVIEW, "Under review"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (DELIVERED, "Delivered"),
    ]
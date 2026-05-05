from __future__ import annotations


class AdminOverrideType:
    """
    Dangerous admin actions that require audit trail.
    """

    FORCE_MARK_FUNDED = "force_mark_funded"
    FORCE_UNLOCK_DELIVERY = "force_unlock_delivery"
    FORCE_COMPLETE = "force_complete"
    MANUAL_PRICE_ADJUSTMENT = "manual_price_adjustment"
    MANUAL_FUNDING_ADJUSTMENT = "manual_funding_adjustment"
    CANCEL_FUNDING_PLAN = "cancel_funding_plan"
    WAIVE_MILESTONE = "waive_milestone"

    CHOICES = [
        (FORCE_MARK_FUNDED, "Force mark funded"),
        (FORCE_UNLOCK_DELIVERY, "Force unlock delivery"),
        (FORCE_COMPLETE, "Force complete"),
        (MANUAL_PRICE_ADJUSTMENT, "Manual price adjustment"),
        (MANUAL_FUNDING_ADJUSTMENT, "Manual funding adjustment"),
        (CANCEL_FUNDING_PLAN, "Cancel funding plan"),
        (WAIVE_MILESTONE, "Waive milestone"),
    ]


class AdminOverrideStatus:
    """
    Approval lifecycle for admin overrides.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    REVERSED = "reversed"

    CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (APPLIED, "Applied"),
        (REVERSED, "Reversed"),
    ]
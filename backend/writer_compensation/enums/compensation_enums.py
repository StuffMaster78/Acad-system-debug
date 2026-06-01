"""
writer_compensation/enums/compensation_enums.py

SINGLE SOURCE OF TRUTH for all enums in this app.
Delete financial_event_enums.py and point every import here.

Convention: UPPERCASE db values throughout for consistency.
"""

from django.db import models


# ---------------------------------------------------------------------------
# Financial event
# ---------------------------------------------------------------------------

from django.db import models


class EventType(models.TextChoices):
    # -----------------------------
    # CORE EARNINGS (work output)
    # -----------------------------
    BASE_EARNING = "BASE_EARNING", "Base earning"
    ORDER_EARNING = "ORDER_EARNING", "Order earning"
    CLASS_EARNING = "CLASS_EARNING", "Class earning"
    SPECIAL_ORDER_EARNING = "SPECIAL_ORDER_EARNING", "Special order earning"

    # -----------------------------
    # INCENTIVES (positive boosts)
    # -----------------------------
    TIP = "TIP", "Tip"
    BONUS = "BONUS", "Generic bonus"
    PERFORMANCE_BONUS = "PERFORMANCE_BONUS", "Performance bonus"
    MILESTONE_BONUS = "MILESTONE_BONUS", "Milestone bonus"
    REFERRAL_BONUS = "REFERRAL_BONUS", "Referral Bonus"
    RETENTION_BONUS = "RETENTION_BONUS", "Retention Bonus"
    REPUTATION_BONUS = "REPUTATION_BONUS", "Reputation Bonus"
    TRUST_SCORE_UPDATED = "TRUST_SCORE_UPDATED", "Trust Score Updated"

    # -----------------------------
    # DEDUCTIONS (permanent loss)
    # -----------------------------
    FINE = "FINE", "Fine"
    DEDUCTION = "DEDUCTION", "Deduction"
    PENALTY = "PENALTY", "Penalty deduction"
    REFUND_DEDUCTION = "REFUND_DEDUCTION", "Refund deduction"

    # -----------------------------
    # TEMPORARY HOLDS (not final)
    # -----------------------------
    REVISION_HOLD = "REVISION_HOLD", "Revision hold"
    DISPUTE_HOLD = "DISPUTE_HOLD", "Dispute hold"
    CANCELLATION = "CANCELLATION", "Cancellation hold"

    # -----------------------------
    # CASH FLOW OPERATIONS
    # -----------------------------
    ADVANCE = "ADVANCE", "Advance payment"
    ADVANCE_RECOVERY = "ADVANCE_RECOVERY", "Advance recovery"

    # -----------------------------
    # SYSTEM OPERATIONS
    # -----------------------------
    ADJUSTMENT = "ADJUSTMENT", "Manual adjustment"
    REVERSAL = "REVERSAL", "Reversal"

class EventStatus(models.TextChoices):
    """
    Lifecycle of a single CompensationEvent.

    PENDING_CONFIRMATION -> just created, awaiting maturity
    MATURED -> confirmed, eligible for settlement
    DEFERRED -> held back (dispute / revision / risk)
    INCLUDED_IN_SETTLEMENT -> picked up by a SettlementPeriod
    PAID -> underlying payout record marked paid
    REVERSED -> cancelled by a REVERSAL event
    VOIDED -> admin-voided, not paid
    DISPUTED -> under dispute review
    ON_HOLD -> manual admin hold
    """
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION", "Pending Confirmation"
    MATURED = "MATURED", "Matured"
    DEFERRED = "DEFERRED", "Deferred"
    INCLUDED_IN_SETTLEMENT = "INCLUDED_IN_SETTLEMENT", "Included In Settlement"
    PAID = "PAID", "Paid"
    REVERSED = "REVERSED", "Reversed"
    VOIDED = "VOIDED", "Voided"
    DISPUTED = "DISPUTED", "Disputed"
    ON_HOLD = "ON_HOLD", "On Hold"


class EventSource(models.TextChoices):
    ORDER = "ORDER", "Order"
    SPECIAL_ORDER = "SPECIAL_ORDER", "Special Order"
    CLASS = "CLASS", "Class"
    TIP = "TIP", "Tip"
    BONUS = "BONUS", "Bonus"
    FINE = "FINE", "Fine"
    MANUAL = "MANUAL", "Manual"


# ---------------------------------------------------------------------------
# Payment window
# ---------------------------------------------------------------------------

class WindowType(models.TextChoices):
    BIWEEKLY = "BIWEEKLY", "Bi-weekly"
    MONTHLY = "MONTHLY", "Monthly"


CycleType = WindowType


class WindowStatus(models.TextChoices):
    """
    One-way lifecycle. Never reversed.
    UPCOMING -> created in advance, not yet open
    OPEN -> accepting events
    CLOSED -> period ended; batch created; no new events
    PROCESSING -> admin clicked Process; writers see status message; events locked
    DONE -> admin finished; held records remain open
    """
    UPCOMING = "UPCOMING", "Upcoming"
    OPEN = "OPEN", "Open"
    CLOSED = "CLOSED", "Closed"
    PROCESSING = "PROCESSING", "Processing"
    DONE = "DONE", "Done"


# ---------------------------------------------------------------------------
# Settlement
# ---------------------------------------------------------------------------

class SettlementStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    LOCKED = "LOCKED", "Locked"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


# ---------------------------------------------------------------------------
# Payout batch
# ---------------------------------------------------------------------------

class PayoutBatchStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    READY = "READY", "Ready"
    PROCESSING = "PROCESSING", "Processing"
    PARTIALLY_CLEARED = "PARTIALLY_CLEARED", "Partially Cleared"
    CLEARED = "CLEARED", "Cleared"
    FAILED = "FAILED", "Failed"


# ---------------------------------------------------------------------------
# Payout record (per-writer line in a batch)
# ---------------------------------------------------------------------------

class PayoutRecordStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    HELD = "HELD", "Held"
    DEFERRED = "DEFERRED", "Deferred"
    PAID = "PAID", "Paid"
    FAILED = "FAILED", "Failed"


# ---------------------------------------------------------------------------
# Advance payments
# ---------------------------------------------------------------------------

class AdvancePaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    RECOVERED = "RECOVERED", "Recovered"
    PARTIALLY_RECOVERED = "PARTIALLY_RECOVERED", "Partially Recovered"


# ---------------------------------------------------------------------------
# Cycle / window change request
# ---------------------------------------------------------------------------

class CycleChangeStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


# ---------------------------------------------------------------------------
# Adjustments
# ---------------------------------------------------------------------------

class AdjustmentType(models.TextChoices):
    BONUS = "BONUS", "Bonus"
    DEDUCTION = "DEDUCTION", "Deduction"
    CORRECTION = "CORRECTION", "Correction"
    MANUAL = "MANUAL", "Manual"


# ---------------------------------------------------------------------------
# Deferral
# ---------------------------------------------------------------------------

class DeferralReason(models.TextChoices):
    DISPUTE = "DISPUTE", "Dispute"
    REVISION = "REVISION", "Revision"
    CLIENT_RISK = "CLIENT_RISK", "Client Risk"
    QUALITY_REVIEW = "QUALITY_REVIEW", "Quality Review"
    MANUAL_REVIEW = "MANUAL_REVIEW", "Manual Review"
    FRAUD_REVIEW = "FRAUD_REVIEW", "Fraud Review"


# ---------------------------------------------------------------------------
# Wallet
# ---------------------------------------------------------------------------

class WalletTransactionType(models.TextChoices):
    CREDIT = "CREDIT", "Credit"
    DEBIT = "DEBIT", "Debit"
    PAYOUT = "PAYOUT", "Payout"
    ADVANCE = "ADVANCE", "Advance"
    ADJUSTMENT = "ADJUSTMENT", "Adjustment"
    REVERSAL = "REVERSAL", "Reversal"


# ---------------------------------------------------------------------------
# Semantic groupings (use in service layer, not in DB)
# ---------------------------------------------------------------------------

EARNING_EVENT_TYPES = {
    EventType.ORDER_EARNING,
    EventType.CLASS_EARNING,
    EventType.SPECIAL_ORDER_EARNING,
    EventType.TIP,
    EventType.BONUS,
    EventType.ADVANCE,
    EventType.PERFORMANCE_BONUS,
    EventType.MILESTONE_BONUS,
    EventType.REFERRAL_BONUS,
    EventType.RETENTION_BONUS,
}

BONUS_EVENT_TYPES = {
    EventType.BONUS,
    EventType.PERFORMANCE_BONUS,
    EventType.MILESTONE_BONUS,
    EventType.REFERRAL_BONUS,
    EventType.RETENTION_BONUS,
    EventType.REPUTATION_BONUS,
}

DEDUCTION_EVENT_TYPES = {
    EventType.FINE,
    EventType.DEDUCTION,
    EventType.REVERSAL,
    EventType.REFUND_DEDUCTION,
    EventType.ADVANCE_RECOVERY,
    EventType.CANCELLATION,
    EventType.DISPUTE_HOLD,
}

HOLD_EVENT_TYPES = {
    EventType.REVISION_HOLD,
    EventType.DISPUTE_HOLD,
}

# Statuses that count toward a writer's payable balance
BALANCE_AFFECTING_STATUSES = {
    EventStatus.MATURED,
    EventStatus.INCLUDED_IN_SETTLEMENT,
    EventStatus.PAID,
}

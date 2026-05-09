from django.db import models


class FinancialEventType(models.TextChoices):
    ORDER_EARNING = "ORDER_EARNING", "Order Earning"
    SPECIAL_ORDER_EARNING = (
        "SPECIAL_ORDER_EARNING",
        "Special Order Earning",
    )
    CLASS_EARNING = "CLASS_EARNING", "Class Earning"

    TIP = "TIP", "Tip"
    BONUS = "BONUS", "Bonus"

    FINE = "FINE", "Fine"
    DEDUCTION = "DEDUCTION", "Deduction"
    ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    ADVANCE_PAYMENT = "ADVANCE_PAYMENT", "Advance Payment"
    ADVANCE_RECOVERY = "ADVANCE_RECOVERY", "Advance Recovery"

    REVISION_HOLD = "REVISION_HOLD", "Revision Hold"
    DISPUTE_HOLD = "DISPUTE_HOLD", "Dispute Hold"

    REVERSAL = "REVERSAL", "Reversal"
    REFUND_DEDUCTION = (
        "REFUND_DEDUCTION",
        "Refund Deduction",
    )


class FinancialEventStatus(models.TextChoices):
    PENDING_CONFIRMATION = (
        "PENDING_CONFIRMATION",
        "Pending Confirmation",
    )

    MATURED = "MATURED", "Matured"

    DEFERRED = "DEFERRED", "Deferred"

    INCLUDED_IN_SETTLEMENT = (
        "INCLUDED_IN_SETTLEMENT",
        "Included In Settlement",
    )

    PAID = "PAID", "Paid"

    REVERSED = "REVERSED", "Reversed"

    VOIDED = "VOIDED", "Voided"

    DISPUTED = "DISPUTED", "Disputed"

    ON_HOLD = "ON_HOLD", "On Hold"


class FinancialEventSource(models.TextChoices):
    ORDER = "ORDER", "Order"

    SPECIAL_ORDER = (
        "SPECIAL_ORDER",
        "Special Order",
    )

    CLASS = "CLASS", "Class"

    TIP = "TIP", "Tip"

    BONUS = "BONUS", "Bonus"

    FINE = "FINE", "Fine"

    MANUAL = "MANUAL", "Manual"


class SettlementStatus(models.TextChoices):
    OPEN = "OPEN", "Open"

    LOCKED = "LOCKED", "Locked"

    PROCESSING = "PROCESSING", "Processing"

    COMPLETED = "COMPLETED", "Completed"

    FAILED = "FAILED", "Failed"


class PaymentWindowType(models.TextChoices):
    BIWEEKLY = "BIWEEKLY", "Biweekly"

    MONTHLY = "MONTHLY", "Monthly"


class PaymentWindowStatus(models.TextChoices):
    UPCOMING = "UPCOMING", "Upcoming"

    OPEN = "OPEN", "Open"

    CLOSED = "CLOSED", "Closed"

    LOCKED = "LOCKED", "Locked"


class PayoutBatchStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"

    READY = "READY", "Ready"

    PROCESSING = "PROCESSING", "Processing"

    PARTIALLY_CLEARED = (
        "PARTIALLY_CLEARED",
        "Partially Cleared",
    )

    CLEARED = "CLEARED", "Cleared"

    FAILED = "FAILED", "Failed"


class PayoutRecordStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"

    APPROVED = "APPROVED", "Approved"

    HELD = "HELD", "Held"

    DEFERRED = "DEFERRED", "Deferred"

    CLEARED = "CLEARED", "Cleared"

    FAILED = "FAILED", "Failed"


class AdvancePaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"

    APPROVED = "APPROVED", "Approved"

    REJECTED = "REJECTED", "Rejected"

    RECOVERED = "RECOVERED", "Recovered"

    PARTIALLY_RECOVERED = (
        "PARTIALLY_RECOVERED",
        "Partially Recovered",
    )


class WalletTransactionType(models.TextChoices):
    CREDIT = "CREDIT", "Credit"

    DEBIT = "DEBIT", "Debit"

    PAYOUT = "PAYOUT", "Payout"

    ADVANCE = "ADVANCE", "Advance"

    ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    REVERSAL = "REVERSAL", "Reversal"


class AdjustmentType(models.TextChoices):
    BONUS = "BONUS", "Bonus"

    DEDUCTION = "DEDUCTION", "Deduction"

    CORRECTION = "CORRECTION", "Correction"

    MANUAL = "MANUAL", "Manual"


class DeferralReason(models.TextChoices):
    DISPUTE = "DISPUTE", "Dispute"

    REVISION = "REVISION", "Revision"

    CLIENT_RISK = "CLIENT_RISK", "Client Risk"

    QUALITY_REVIEW = "QUALITY_REVIEW", "Quality Review"

    MANUAL_REVIEW = "MANUAL_REVIEW", "Manual Review"

    FRAUD_REVIEW = "FRAUD_REVIEW", "Fraud Review"


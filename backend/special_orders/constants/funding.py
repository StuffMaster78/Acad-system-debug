from __future__ import annotations


class FundingPlanStatus:
    """
    Financial funding status for a special order.
    """

    DRAFT = "draft"
    AWAITING_DEPOSIT = "awaiting_deposit"
    PARTIALLY_FUNDED = "partially_funded"
    FUNDED = "funded"
    PARTIALLY_REFUNDED = "partially_refunded"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

    CHOICES = [
        (DRAFT, "Draft"),
        (AWAITING_DEPOSIT, "Awaiting deposit"),
        (PARTIALLY_FUNDED, "Partially funded"),
        (FUNDED, "Funded"),
        (PARTIALLY_REFUNDED, "Partially refunded"),
        (REFUNDED, "Refunded"),
        (CANCELLED, "Cancelled"),
    ]


class FundingMilestoneStatus:
    """
    Funding status for one milestone.
    """

    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    CHOICES = [
        (PENDING, "Pending"),
        (PARTIALLY_PAID, "Partially paid"),
        (PAID, "Paid"),
        (OVERDUE, "Overdue"),
        (CANCELLED, "Cancelled"),
        (REFUNDED, "Refunded"),
    ]


class FundingMilestoneType:
    """
    Purpose of a funding milestone.
    """

    DEPOSIT = "deposit"
    PROGRESS = "progress"
    FINAL = "final"
    CHANGE_REQUEST = "change_request"
    MANUAL = "manual"

    CHOICES = [
        (DEPOSIT, "Deposit"),
        (PROGRESS, "Progress"),
        (FINAL, "Final"),
        (CHANGE_REQUEST, "Change request"),
        (MANUAL, "Manual"),
    ]


class PaymentApplicationSource:
    """
    Source of funds applied to a special order.
    """

    WALLET = "wallet"
    EXTERNAL = "external"
    SPLIT = "split"
    ADMIN_ADJUSTMENT = "admin_adjustment"

    CHOICES = [
        (WALLET, "Wallet"),
        (EXTERNAL, "External"),
        (SPLIT, "Split"),
        (ADMIN_ADJUSTMENT, "Admin adjustment"),
    ]


class PaymentApplicationStatus:
    """
    Status of a payment application.
    """

    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    REVERSED = "reversed"

    CHOICES = [
        (PENDING, "Pending"),
        (APPLIED, "Applied"),
        (FAILED, "Failed"),
        (REVERSED, "Reversed"),
    ]


class RefundApplicationStatus:
    """
    Status of a refund application.
    """

    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    REFUNDED = "refunded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (PROCESSING, "Processing"),
        (REFUNDED, "Refunded"),
        (FAILED, "Failed"),
        (CANCELLED, "Cancelled"),
    ]


class RefundDestination:
    """
    Where the refund should go.
    """

    WALLET = "wallet"
    ORIGINAL_PAYMENT_METHOD = "original_payment_method"
    MANUAL = "manual"

    CHOICES = [
        (WALLET, "Wallet"),
        (ORIGINAL_PAYMENT_METHOD, "Original payment method"),
        (MANUAL, "Manual"),
    ]
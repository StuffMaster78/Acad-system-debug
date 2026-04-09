from django.db import models


class WalletType(models.TextChoices):
    CLIENT = "client", "Client"
    WRITER = "writer", "Writer"


class WalletStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    CLOSED = "closed", "Closed"


class WalletEntryDirection(models.TextChoices):
    CREDIT = "credit", "Credit"
    DEBIT = "debit", "Debit"


class WalletEntryStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    POSTED = "posted", "Posted"
    REVERSED = "reversed", "Reversed"
    FAILED = "failed", "Failed"


class WalletEntryType(models.TextChoices):
    FUNDING = "funding", "Funding"
    ORDER_PAYMENT = "order_payment", "Order Payment"
    ORDER_REFUND = "order_refund", "Order Refund"
    EARNING = "earning", "Earning"
    BONUS = "bonus", "Bonus"
    PENALTY = "penalty", "Penalty"
    ADMIN_ADJUSTMENT = "admin_adjustment", "Admin Adjustment"
    ADMIN_CREDIT = "admin_credit", "Admin Credit"
    ADMIN_DEBIT = "admin_debit", "Admin Debit"
    HOLD = "hold", "Hold"
    HOLD_RELEASE = "hold_release", "Hold Release"
    HOLD_CAPTURE = "hold_capture", "Hold Capture"
    PAYOUT_RESERVE = "payout_reserve", "Payout Reserve"
    PAYOUT_RELEASE = "payout_release", "Payout Release"
    PAYOUT_SETTLED = "payout_settled", "Payout Settled"


class WalletHoldStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CAPTURED = "captured", "Captured"
    RELEASED = "released", "Released"
    EXPIRED = "expired", "Expired"
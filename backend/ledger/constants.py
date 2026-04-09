from django.db import models


class LedgerAccountType(models.TextChoices):
    ASSET = "asset", "Asset"
    LIABILITY = "liability", "Liability"
    EQUITY = "equity", "Equity"
    REVENUE = "revenue", "Revenue"
    EXPENSE = "expense", "Expense"
    CLEARING = "clearing", "Clearing"
    CONTROL = "control", "Control"


class LedgerAccountStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ARCHIVED = "archived", "Archived"


class JournalEntryStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    POSTED = "posted", "Posted"
    REVERSED = "reversed", "Reversed"
    FAILED = "failed", "Failed"


class EntrySide(models.TextChoices):
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"


class LedgerEntryType(models.TextChoices):
    WALLET_TOP_UP = "wallet_top_up", "Wallet Top Up"
    WALLET_DEBIT = "wallet_debit", "Wallet Debit"
    WALLET_CREDIT = "wallet_credit", "Wallet Credit"
    WALLET_HOLD = "wallet_hold", "Wallet Hold"
    WALLET_HOLD_RELEASE = "wallet_hold_release", "Wallet Hold Release"
    WALLET_HOLD_CAPTURE = "wallet_hold_capture", "Wallet Hold Capture"

    ORDER_PAYMENT = "order_payment", "Order Payment"
    ORDER_INSTALLMENT_PAYMENT = (
        "order_installment_payment",
        "Order Installment Payment",
    )

    SPECIAL_ORDER_DEPOSIT = "special_order_deposit", "Special Order Deposit"
    SPECIAL_ORDER_INSTALLMENT = (
        "special_order_installment",
        "Special Order Installment",
    )

    CLASS_BUNDLE_DEPOSIT = "class_bundle_deposit", "Class Bundle Deposit"
    CLASS_BUNDLE_INSTALLMENT = (
        "class_bundle_installment",
        "Class Bundle Installment",
    )
    CLASS_PAYMENT = "class_payment", "Class Payment"

    EXTERNAL_PAYMENT_CAPTURE = (
        "external_payment_capture",
        "External Payment Capture",
    )
    SPLIT_PAYMENT_CAPTURE = "split_payment_capture", "Split Payment Capture"
    PAYMENT_REVERSAL = "payment_reversal", "Payment Reversal"
    PAYMENT_FEE = "payment_fee", "Payment Fee"

    REFUND_TO_WALLET = "refund_to_wallet", "Refund To Wallet"
    REFUND_EXTERNAL = "refund_external", "External Refund"
    REFUND_REVERSAL = "refund_reversal", "Refund Reversal"

    WRITER_EARNING_ACCRUAL = (
        "writer_earning_accrual",
        "Writer Earning Accrual",
    )
    WRITER_PAYOUT = "writer_payout", "Writer Payout"
    WRITER_PAYOUT_REVERSAL = (
        "writer_payout_reversal",
        "Writer Payout Reversal",
    )
    WRITER_FINE = "writer_fine", "Writer Fine"
    WRITER_FINE_REVERSAL = "writer_fine_reversal", "Writer Fine Reversal"
    WRITER_BONUS = "writer_bonus", "Writer Bonus"
    WRITER_ADJUSTMENT = "writer_adjustment", "Writer Adjustment"

    DISPUTE_HOLD = "dispute_hold", "Dispute Hold"
    DISPUTE_RELEASE = "dispute_release", "Dispute Release"
    DISPUTE_REVERSAL = "dispute_reversal", "Dispute Reversal"

    MANUAL_CREDIT = "manual_credit", "Manual Credit"
    MANUAL_DEBIT = "manual_debit", "Manual Debit"
    MANUAL_ADJUSTMENT = "manual_adjustment", "Manual Adjustment"

    GATEWAY_SETTLEMENT = "gateway_settlement", "Gateway Settlement"
    GATEWAY_RECONCILIATION_ADJUSTMENT = (
        "gateway_reconciliation_adjustment",
        "Gateway Reconciliation Adjustment",
    )


class HoldStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CAPTURED = "captured", "Captured"
    RELEASED = "released", "Released"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"


class ReconciliationStatus(models.TextChoices):
    UNRECONCILED = "unreconciled", "Unreconciled"
    MATCHED = "matched", "Matched"
    PARTIALLY_MATCHED = "partially_matched", "Partially Matched"
    MISMATCHED = "mismatched", "Mismatched"
    RESOLVED = "resolved", "Resolved"


class SourceApp(models.TextChoices):
    ORDERS = "orders", "Orders"
    SPECIAL_ORDERS = "special_orders", "Special Orders"
    CLASS_MANAGEMENT = "class_management", "Class Management"
    PAYMENTS = "payments", "Payments"
    WALLETS = "wallets", "Wallets"
    REFUNDS = "refunds", "Refunds"
    DISPUTES = "disputes", "Disputes"
    FINES = "fines", "Fines"
    WRITER_PAYMENTS = "writer_payments", "Writer Payments"
    ADMIN = "admin", "Admin"
    SYSTEM = "system", "System"


SYSTEM_ACCOUNT_CODES = {
    "platform_cash": "PLATFORM_CASH",
    "gateway_clearing": "GATEWAY_CLEARING",
    "client_wallet_liability": "CLIENT_WALLET_LIABILITY",
    "writer_payable": "WRITER_PAYABLE",
    "platform_revenue": "PLATFORM_REVENUE",
    "refund_reserve": "REFUND_RESERVE",
    "dispute_holds": "DISPUTE_HOLDS",
    "fines_recovery": "FINES_RECOVERY",
    "wallet_holds_control": "WALLET_HOLDS_CONTROL",
    "manual_adjustments": "MANUAL_ADJUSTMENTS",
}


ACCOUNT_TYPES_REQUIRING_STRICT_BALANCE = {
    LedgerAccountType.ASSET,
    LedgerAccountType.LIABILITY,
    LedgerAccountType.EQUITY,
    LedgerAccountType.CLEARING,
    LedgerAccountType.CONTROL,
}


FINAL_JOURNAL_ENTRY_STATUSES = {
    JournalEntryStatus.POSTED,
    JournalEntryStatus.REVERSED,
    JournalEntryStatus.FAILED,
}


MUTABLE_JOURNAL_ENTRY_STATUSES = {
    JournalEntryStatus.DRAFT,
    JournalEntryStatus.PENDING,
}


HOLD_FINAL_STATUSES = {
    HoldStatus.CAPTURED,
    HoldStatus.RELEASED,
    HoldStatus.EXPIRED,
    HoldStatus.CANCELLED,
}


RECONCILIATION_FINAL_STATUSES = {
    ReconciliationStatus.MATCHED,
    ReconciliationStatus.RESOLVED,
}


DEBIT_NORMAL_ACCOUNT_TYPES = {
    LedgerAccountType.ASSET,
    LedgerAccountType.EXPENSE,
    LedgerAccountType.CLEARING,
    LedgerAccountType.CONTROL,
}


CREDIT_NORMAL_ACCOUNT_TYPES = {
    LedgerAccountType.LIABILITY,
    LedgerAccountType.EQUITY,
    LedgerAccountType.REVENUE,
}


ENTRY_TYPES_REQUIRING_EXTERNAL_REFERENCE = {
    LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE,
    LedgerEntryType.SPLIT_PAYMENT_CAPTURE,
    LedgerEntryType.REFUND_EXTERNAL,
    LedgerEntryType.GATEWAY_SETTLEMENT,
    LedgerEntryType.GATEWAY_RECONCILIATION_ADJUSTMENT,
    LedgerEntryType.WRITER_PAYOUT,
}


ENTRY_TYPES_ALLOWED_FOR_HOLDS = {
    LedgerEntryType.WALLET_HOLD,
    LedgerEntryType.WALLET_HOLD_RELEASE,
    LedgerEntryType.WALLET_HOLD_CAPTURE,
    LedgerEntryType.DISPUTE_HOLD,
    LedgerEntryType.DISPUTE_RELEASE,
}


ENTRY_TYPES_REQUIRING_SOURCE_REFERENCE = {
    LedgerEntryType.ORDER_PAYMENT,
    LedgerEntryType.ORDER_INSTALLMENT_PAYMENT,
    LedgerEntryType.SPECIAL_ORDER_DEPOSIT,
    LedgerEntryType.SPECIAL_ORDER_INSTALLMENT,
    LedgerEntryType.CLASS_BUNDLE_DEPOSIT,
    LedgerEntryType.CLASS_BUNDLE_INSTALLMENT,
    LedgerEntryType.CLASS_PAYMENT,
    LedgerEntryType.REFUND_TO_WALLET,
    LedgerEntryType.REFUND_EXTERNAL,
    LedgerEntryType.WRITER_EARNING_ACCRUAL,
    LedgerEntryType.WRITER_PAYOUT,
    LedgerEntryType.WRITER_FINE,
    LedgerEntryType.DISPUTE_HOLD,
    LedgerEntryType.DISPUTE_RELEASE,
}


ENTRY_TYPES_THAT_MOVE_CLIENT_WALLET = {
    LedgerEntryType.WALLET_TOP_UP,
    LedgerEntryType.WALLET_DEBIT,
    LedgerEntryType.WALLET_CREDIT,
    LedgerEntryType.WALLET_HOLD,
    LedgerEntryType.WALLET_HOLD_RELEASE,
    LedgerEntryType.WALLET_HOLD_CAPTURE,
    LedgerEntryType.REFUND_TO_WALLET,
    LedgerEntryType.SPLIT_PAYMENT_CAPTURE,
}


ENTRY_TYPES_THAT_MOVE_WRITER_BALANCE = {
    LedgerEntryType.WRITER_EARNING_ACCRUAL,
    LedgerEntryType.WRITER_PAYOUT,
    LedgerEntryType.WRITER_PAYOUT_REVERSAL,
    LedgerEntryType.WRITER_FINE,
    LedgerEntryType.WRITER_FINE_REVERSAL,
    LedgerEntryType.WRITER_BONUS,
    LedgerEntryType.WRITER_ADJUSTMENT,
}


DEFAULT_ENTRY_DESCRIPTION_MAP = {
    LedgerEntryType.WALLET_TOP_UP: "Wallet top up recorded",
    LedgerEntryType.WALLET_DEBIT: "Wallet debit recorded",
    LedgerEntryType.WALLET_CREDIT: "Wallet credit recorded",
    LedgerEntryType.WALLET_HOLD: "Wallet funds placed on hold",
    LedgerEntryType.WALLET_HOLD_RELEASE: "Wallet hold released",
    LedgerEntryType.WALLET_HOLD_CAPTURE: "Wallet hold captured",
    LedgerEntryType.ORDER_PAYMENT: "Order payment recorded",
    LedgerEntryType.ORDER_INSTALLMENT_PAYMENT: (
        "Order installment payment recorded"
    ),
    LedgerEntryType.SPECIAL_ORDER_DEPOSIT: (
        "Special order deposit recorded"
    ),
    LedgerEntryType.SPECIAL_ORDER_INSTALLMENT: (
        "Special order installment recorded"
    ),
    LedgerEntryType.CLASS_BUNDLE_DEPOSIT: (
        "Class bundle deposit recorded"
    ),
    LedgerEntryType.CLASS_BUNDLE_INSTALLMENT: (
        "Class bundle installment recorded"
    ),
    LedgerEntryType.CLASS_PAYMENT: "Class payment recorded",
    LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE: (
        "External payment capture recorded"
    ),
    LedgerEntryType.SPLIT_PAYMENT_CAPTURE: "Split payment capture recorded",
    LedgerEntryType.PAYMENT_REVERSAL: "Payment reversal recorded",
    LedgerEntryType.PAYMENT_FEE: "Payment fee recorded",
    LedgerEntryType.REFUND_TO_WALLET: "Refund to wallet recorded",
    LedgerEntryType.REFUND_EXTERNAL: "External refund recorded",
    LedgerEntryType.REFUND_REVERSAL: "Refund reversal recorded",
    LedgerEntryType.WRITER_EARNING_ACCRUAL: (
        "Writer earning accrual recorded"
    ),
    LedgerEntryType.WRITER_PAYOUT: "Writer payout recorded",
    LedgerEntryType.WRITER_PAYOUT_REVERSAL: (
        "Writer payout reversal recorded"
    ),
    LedgerEntryType.WRITER_FINE: "Writer fine recorded",
    LedgerEntryType.WRITER_FINE_REVERSAL: "Writer fine reversal recorded",
    LedgerEntryType.WRITER_BONUS: "Writer bonus recorded",
    LedgerEntryType.WRITER_ADJUSTMENT: "Writer adjustment recorded",
    LedgerEntryType.DISPUTE_HOLD: "Dispute hold recorded",
    LedgerEntryType.DISPUTE_RELEASE: "Dispute release recorded",
    LedgerEntryType.DISPUTE_REVERSAL: "Dispute reversal recorded",
    LedgerEntryType.MANUAL_CREDIT: "Manual credit recorded",
    LedgerEntryType.MANUAL_DEBIT: "Manual debit recorded",
    LedgerEntryType.MANUAL_ADJUSTMENT: "Manual adjustment recorded",
    LedgerEntryType.GATEWAY_SETTLEMENT: "Gateway settlement recorded",
    LedgerEntryType.GATEWAY_RECONCILIATION_ADJUSTMENT: (
        "Gateway reconciliation adjustment recorded"
    ),
}
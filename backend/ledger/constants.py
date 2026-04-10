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
    CLIENT_WALLET_TOP_UP = (
        "client_wallet_top_up",
        "Client Wallet Top Up",
    )
    CLIENT_WALLET_SPEND = (
        "client_wallet_spend",
        "Client Wallet Spend",
    )
    CLIENT_WALLET_SUPPORT_CREDIT = (
        "client_wallet_support_credit",
        "Client Wallet Support Credit",
    )
    CLIENT_WALLET_SUPPORT_DEBIT = (
        "client_wallet_support_debit",
        "Client Wallet Support Debit",
    )
    CLIENT_WALLET_REFUND = (
        "client_wallet_refund",
        "Client Wallet Refund",
    )
    CLIENT_WALLET_TIP_DEDUCTION = (
        "client_wallet_tip_deduction",
        "Client Wallet Tip Deduction",
    )

    EXTERNAL_PAYMENT_CAPTURE = (
        "external_payment_capture",
        "External Payment Capture",
    )
    EXTERNAL_REFUND = (
        "external_refund",
        "External Refund",
    )
    PAYMENT_REVERSAL = "payment_reversal", "Payment Reversal"
    PAYMENT_FEE = "payment_fee", "Payment Fee"
    GATEWAY_SETTLEMENT = (
        "gateway_settlement",
        "Gateway Settlement",
    )
    GATEWAY_RECONCILIATION_ADJUSTMENT = (
        "gateway_reconciliation_adjustment",
        "Gateway Reconciliation Adjustment",
    )

    ORDER_PAYMENT = "order_payment", "Order Payment"
    ORDER_INSTALLMENT_PAYMENT = (
        "order_installment_payment",
        "Order Installment Payment",
    )
    SPECIAL_ORDER_DEPOSIT = (
        "special_order_deposit",
        "Special Order Deposit",
    )
    SPECIAL_ORDER_INSTALLMENT = (
        "special_order_installment",
        "Special Order Installment",
    )
    CLASS_BUNDLE_DEPOSIT = (
        "class_bundle_deposit",
        "Class Bundle Deposit",
    )
    CLASS_BUNDLE_INSTALLMENT = (
        "class_bundle_installment",
        "Class Bundle Installment",
    )
    CLASS_PAYMENT = "class_payment", "Class Payment"

    WRITER_EARNING_ACCRUAL = (
        "writer_earning_accrual",
        "Writer Earning Accrual",
    )
    WRITER_PAYOUT = "writer_payout", "Writer Payout"
    WRITER_BONUS = "writer_bonus", "Writer Bonus"
    WRITER_FINE = "writer_fine", "Writer Fine"
    WRITER_TIP_CREDIT = (
        "writer_tip_credit",
        "Writer Tip Credit",
    )
    WRITER_MANUAL_INCREASE = (
        "writer_manual_increase",
        "Writer Manual Increase",
    )
    WRITER_MANUAL_DECREASE = (
        "writer_manual_decrease",
        "Writer Manual Decrease",
    )
    WRITER_EARNING_RECOVERY = (
        "writer_earning_recovery",
        "Writer Earning Recovery",
    )
    WRITER_EARNING_RESTORATION = (
        "writer_earning_restoration",
        "Writer Earning Restoration",
    )
    WRITER_RECOVERY_APPLIED_TO_PAYOUT = (
        "writer_recovery_applied_to_payout",
        "Writer Recovery Applied To Payout",
    )
    DISPUTE_HOLD = "dispute_hold", "Dispute Hold"
    DISPUTE_RELEASE = "dispute_release", "Dispute Release"
    DISPUTE_REVERSAL = "dispute_reversal", "Dispute Reversal"

    MANUAL_ADJUSTMENT = "manual_adjustment", "Manual Adjustment"


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
    PAYMENT_PROCESSOR = "payment_processor", "Payment Processor"
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
    "client_platform_credit": "CLIENT_PLATFORM_CREDIT",
    "client_credit_consumption": "CLIENT_CREDIT_CONSUMPTION",
    "writer_payable": "WRITER_PAYABLE",
    "writer_tip_payable": "WRITER_TIP_PAYABLE",
    "writer_compensation_expense": "WRITER_COMPENSATION_EXPENSE",
    "writer_bonus_expense": "WRITER_BONUS_EXPENSE",
    "platform_revenue": "PLATFORM_REVENUE",
    "platform_tip_margin": "PLATFORM_TIP_MARGIN",
    "manual_adjustments": "MANUAL_ADJUSTMENTS",
    "fines_recovery": "FINES_RECOVERY",
    "tip_allocation_clearing": "TIP_ALLOCATION_CLEARING",
    "writer_recovery": "WRITER_RECOVERY",
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
    LedgerEntryType.EXTERNAL_REFUND,
    LedgerEntryType.GATEWAY_SETTLEMENT,
    LedgerEntryType.GATEWAY_RECONCILIATION_ADJUSTMENT,
    LedgerEntryType.WRITER_PAYOUT,
}


ENTRY_TYPES_ALLOWED_FOR_HOLDS = {
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
    LedgerEntryType.CLIENT_WALLET_SPEND,
    LedgerEntryType.CLIENT_WALLET_SUPPORT_CREDIT,
    LedgerEntryType.CLIENT_WALLET_SUPPORT_DEBIT,
    LedgerEntryType.CLIENT_WALLET_REFUND,
    LedgerEntryType.CLIENT_WALLET_TIP_DEDUCTION,
    LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE,
    LedgerEntryType.EXTERNAL_REFUND,
    LedgerEntryType.WRITER_EARNING_ACCRUAL,
    LedgerEntryType.WRITER_PAYOUT,
    LedgerEntryType.WRITER_BONUS,
    LedgerEntryType.WRITER_FINE,
    LedgerEntryType.WRITER_TIP_CREDIT,
    LedgerEntryType.WRITER_MANUAL_INCREASE,
    LedgerEntryType.WRITER_MANUAL_DECREASE,
    LedgerEntryType.DISPUTE_HOLD,
    LedgerEntryType.DISPUTE_RELEASE,
}


ENTRY_TYPES_THAT_MOVE_CLIENT_WALLET = {
    LedgerEntryType.CLIENT_WALLET_TOP_UP,
    LedgerEntryType.CLIENT_WALLET_SPEND,
    LedgerEntryType.CLIENT_WALLET_SUPPORT_CREDIT,
    LedgerEntryType.CLIENT_WALLET_SUPPORT_DEBIT,
    LedgerEntryType.CLIENT_WALLET_REFUND,
    LedgerEntryType.CLIENT_WALLET_TIP_DEDUCTION,
}


ENTRY_TYPES_THAT_MOVE_WRITER_BALANCE = {
    LedgerEntryType.WRITER_EARNING_ACCRUAL,
    LedgerEntryType.WRITER_PAYOUT,
    LedgerEntryType.WRITER_BONUS,
    LedgerEntryType.WRITER_FINE,
    LedgerEntryType.WRITER_TIP_CREDIT,
    LedgerEntryType.WRITER_MANUAL_INCREASE,
    LedgerEntryType.WRITER_MANUAL_DECREASE,
}


DEFAULT_ENTRY_DESCRIPTION_MAP = {
    LedgerEntryType.CLIENT_WALLET_TOP_UP: (
        "Client wallet top up recorded"
    ),
    LedgerEntryType.CLIENT_WALLET_SPEND: (
        "Client wallet spend recorded"
    ),
    LedgerEntryType.CLIENT_WALLET_SUPPORT_CREDIT: (
        "Client wallet support credit recorded"
    ),
    LedgerEntryType.CLIENT_WALLET_SUPPORT_DEBIT: (
        "Client wallet support debit recorded"
    ),
    LedgerEntryType.CLIENT_WALLET_REFUND: (
        "Client wallet refund recorded"
    ),
    LedgerEntryType.CLIENT_WALLET_TIP_DEDUCTION: (
        "Client wallet tip deduction recorded"
    ),
    LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE: (
        "External payment capture recorded"
    ),
    LedgerEntryType.EXTERNAL_REFUND: (
        "External refund recorded"
    ),
    LedgerEntryType.PAYMENT_REVERSAL: "Payment reversal recorded",
    LedgerEntryType.PAYMENT_FEE: "Payment fee recorded",
    LedgerEntryType.GATEWAY_SETTLEMENT: "Gateway settlement recorded",
    LedgerEntryType.GATEWAY_RECONCILIATION_ADJUSTMENT: (
        "Gateway reconciliation adjustment recorded"
    ),
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
    LedgerEntryType.WRITER_EARNING_ACCRUAL: (
        "Writer earning accrual recorded"
    ),
    LedgerEntryType.WRITER_PAYOUT: "Writer payout recorded",
    LedgerEntryType.WRITER_BONUS: "Writer bonus recorded",
    LedgerEntryType.WRITER_FINE: "Writer fine recorded",
    LedgerEntryType.WRITER_TIP_CREDIT: "Writer tip credit recorded",
    LedgerEntryType.WRITER_MANUAL_INCREASE: (
        "Writer manual increase recorded"
    ),
    LedgerEntryType.WRITER_MANUAL_DECREASE: (
        "Writer manual decrease recorded"
    ),
    LedgerEntryType.DISPUTE_HOLD: "Dispute hold recorded",
    LedgerEntryType.DISPUTE_RELEASE: "Dispute release recorded",
    LedgerEntryType.DISPUTE_REVERSAL: "Dispute reversal recorded",
    LedgerEntryType.MANUAL_ADJUSTMENT: "Manual adjustment recorded",
}
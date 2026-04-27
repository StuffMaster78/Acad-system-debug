from __future__ import annotations

from django.db import models


class InvoiceStatus(models.TextChoices):
    """
    Enumerate the lifecycle states of an invoice.

    These states describe customer-facing billing state only.
    Payment collection and accounting are handled elsewhere.
    """

    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    PARTIALLY_PAID = "partially_paid", "Partially Paid"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"


class InvoicePurpose(models.TextChoices):
    """
    Enumerate supported business purposes for invoices.

    The purpose explains why the receivable exists. It should not be
    used to control payment provider logic directly.
    """

    ORDER = "order", "Order"
    SPECIAL_ORDER = "special_order", "Special Order"
    CLASS_PURCHASE = "class_purchase", "Class Purchase"
    MANUAL = "manual", "Manual"
    OTHER = "other", "Other"


class PaymentRequestStatus(models.TextChoices):
    """
    Enumerate the lifecycle states of a payment request.

    A payment request is a customer-facing billing request that may
    later produce an invoice or direct settlement flow.
    """

    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    PARTIALLY_PAID = "partially_paid", "Partially Paid"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"


class PaymentRequestPurpose(models.TextChoices):
    """
    Enumerate supported business purposes for payment requests.

    These purposes help classify the request without embedding domain
    workflow logic in the model itself.
    The purpose explains why the receivable exists.
    Useful for filtering, reporting,
    and downstream domain coordination.
    """

    ORDER_PAYMENT = "order_payment", "Order Payment"
    ORDER_EXTRA_CHARGE = "order_extra_charge", "Order Extra Charge"
    SPECIAL_ORDER_PAYMENT = (
        "special_order_payment",
        "Special Order Payment",
    )
    CLASS_PURCHASE = "class_purchase", "Class Purchase"
    MANUAL_BILLING = "manual_billing", "Manual Billing"
    OTHER = "other", "Other"


class ReceiptStatus(models.TextChoices):
    """
    Enumerate the lifecycle states of a receipt.

    Receipts are post-settlement billing artifacts and should remain
    immutable in most cases after issuance.
    """

    ISSUED = "issued", "Issued"
    VOIDED = "voided", "Voided"


class ReminderStatus(models.TextChoices):
    """
    Enumerate the lifecycle states of a reminder record.

    Reminder records track the outcome of reminder attempts rather than
    the lifecycle of the related invoice itself.
    """

    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
from django.db import models


class PaymentProvider(models.TextChoices):
    STRIPE = "stripe", "Stripe"
    PAYPAL = "paypal", "PayPal"
    FLUTTERWAVE = "flutterwave", "Flutterwave"
    BANK = "bank", "Bank"
    MANUAL = "manual", "Manual"


class PaymentIntentStatus(models.TextChoices):
    CREATED = "created", "Created"
    PENDING = "pending", "Pending"
    REQUIRES_ACTION = "requires_action", "Requires Action"
    PROCESSING = "processing", "Processing"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"
    PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"
    REFUNDED = "refunded", "Refunded"
    EXPIRED = "expired", "Expired"


class PaymentTransactionKind(models.TextChoices):
    AUTHORIZATION = "authorization", "Authorization"
    CAPTURE = "capture", "Capture"
    CHARGE = "charge", "Charge"
    REFUND = "refund", "Refund"
    CHARGEBACK = "chargeback", "Chargeback"
    REVERSAL = "reversal", "Reversal"
    WEBHOOK_EVENT = "webhook_event", "Webhook Event"
    MANUAL_CONFIRMATION = "manual_confirmation", "Manual Confirmation"


class PaymentTransactionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"
    DISPUTED = "disputed", "Disputed"
    REFUNDED = "refunded", "Refunded"


class PaymentApplicationStatus(models.TextChoices):
    NOT_APPLIED = "not_applied", "Not Applied"
    APPLYING = "applying", "Applying"
    APPLIED = "applied", "Applied"
    APPLICATION_FAILED = "application_failed", "Application Failed"
    

class WebhookProcessingStatus(models.TextChoices):
    RECEIVED = "received", "Received"
    PROCESSED = "processed", "Processed"
    FAILED = "failed", "Failed"
    IGNORED = "ignored", "Ignored"


class PaymentIntentPurpose(models.TextChoices):
    ORDER = "order", "Order"
    SPECIAL_ORDER = "special_order", "Special Order"
    CLASS_PURCHASE = "class_purchase", "Class Purchase"
    BUNDLE_PURCHASE = "bundle_purchase", "Bundle Purchase"
    WALLET_TOP_UP = "wallet_top_up", "Wallet Top Up"
    TIP = "tip", "Tip"

class PaymentAllocationType(models.TextChoices):
    WALLET = "wallet", "Wallet"
    EXTERNAL_PAYMENT = "external_payment", "External Payment"


class PaymentAllocationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RESERVED = "reserved", "Reserved"
    APPLIED = "applied", "Applied"
    RELEASED = "released", "Released"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"


class PaymentDisputeStatus(models.TextChoices):
    OPEN = "open", "Open"
    UNDER_REVIEW = "under_review", "Under Review"
    WON = "won", "Won"
    LOST = "lost", "Lost"
    CLOSED = "closed", "Closed"


class PaymentRefundStatus(models.TextChoices):
    REQUESTED = "requested", "Requested"
    PENDING = "pending", "Pending"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"


class RefundDestination(models.TextChoices):
    ORIGINAL_METHOD = "original_method", "Original Method"
    WALLET = "wallet", "Wallet"
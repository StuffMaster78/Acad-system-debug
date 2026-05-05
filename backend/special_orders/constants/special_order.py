from __future__ import annotations


class SpecialOrderPricingMode:
    """
    Defines how a special order gets its price.
    """

    FIXED_CONFIG = "fixed_config"
    QUOTED = "quoted"

    CHOICES = [
        (FIXED_CONFIG, "Fixed config"),
        (QUOTED, "Quoted"),
    ]


class SpecialOrderStatus:
    """
    Business lifecycle for a special order.

    This should not be used as financial truth. Funding truth belongs to
    SpecialOrderFundingPlan and SpecialOrderPaymentApplication.
    """

    INQUIRY = "inquiry"
    QUOTE_PENDING = "quote_pending"
    QUOTE_SENT = "quote_sent"
    QUOTE_ACCEPTED = "quote_accepted"
    AWAITING_PAYMENT = "awaiting_payment"
    PARTIALLY_FUNDED = "partially_funded"
    READY_FOR_STAFFING = "ready_for_staffing"
    ASSIGNED = "assigned"
    ON_HOLD = "on_hold"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    READY_FOR_DELIVERY = "ready_for_delivery"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"
    ON_REVISION = "on_revision"
    REFUNDED = "refunded"

    CHOICES = [
        (INQUIRY, "Inquiry"),
        (QUOTE_PENDING, "Quote pending"),
        (QUOTE_SENT, "Quote sent"),
        (QUOTE_ACCEPTED, "Quote accepted"),
        (AWAITING_PAYMENT, "Awaiting payment"),
        (PARTIALLY_FUNDED, "Partially funded"),
        (READY_FOR_STAFFING, "Ready for staffing"),
        (ASSIGNED, "Assigned"),
        (ON_HOLD, "On hold"),
        (SUBMITTED, "Submitted"),
        (IN_PROGRESS, "In progress"),
        (READY_FOR_DELIVERY, "Ready for delivery"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
        (APPROVED, "Approved"),
        (REVISION_REQUESTED, "Revision requested"),
        (ON_REVISION, "On revision"),
        (REFUNDED, "Refunded"),
    ]


class SpecialOrderOrigin:
    """
    Describes where the special order came from.
    """

    CLIENT_REQUEST = "client_request"
    STAFF_CREATED = "staff_created"
    ADMIN_CREATED = "admin_created"
    CONVERTED_FROM_INQUIRY = "converted_from_inquiry"
    MIGRATED_LEGACY = "migrated_legacy"

    CHOICES = [
        (CLIENT_REQUEST, "Client request"),
        (STAFF_CREATED, "Staff created"),
        (ADMIN_CREATED, "Admin created"),
        (CONVERTED_FROM_INQUIRY, "Converted from inquiry"),
        (MIGRATED_LEGACY, "Migrated legacy"),
    ]


class SpecialOrderPriority:
    """
    Operational priority for staff queues.
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

    CHOICES = [
        (LOW, "Low"),
        (NORMAL, "Normal"),
        (HIGH, "High"),
        (URGENT, "Urgent"),
        (CRITICAL, "Critical"),
    ]

class SpecialOrderDifficultyLevel:
    EASY = "easy"
    STANDARD = "standard"
    COMPLEX = "complex"
    HIGHLY_COMPLEX = "highly_complex"

    CHOICES = [
        (EASY, "Easy"),
        (STANDARD, "Standard"),
        (COMPLEX, "Complex"),
        (HIGHLY_COMPLEX, "Highly complex"),
    ]


class SpecialOrderWriterLevel:
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"
    PREMIUM = "premium"

    CHOICES = [
        (STANDARD, "Standard"),
        (ADVANCED, "Advanced"),
        (EXPERT, "Expert"),
        (PREMIUM, "Premium"),
    ]


class SpecialOrderClientTier:
    NEW = "new"
    REGULAR = "regular"
    VIP = "vip"
    ENTERPRISE = "enterprise"

    CHOICES = [
        (NEW, "New"),
        (REGULAR, "Regular"),
        (VIP, "VIP"),
        (ENTERPRISE, "Enterprise"),
    ]
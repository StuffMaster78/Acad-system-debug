from __future__ import annotations


class SpecialOrderQuoteStatus:
    """
    Lifecycle for special order quotes.
    """

    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    CHOICES = [
        (DRAFT, "Draft"),
        (SENT, "Sent"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
    ]


class SpecialOrderQuoteLineType:
    """
    Type of quote line item.
    """

    SERVICE = "service"
    ADDON = "addon"
    URGENCY_FEE = "urgency_fee"
    COMPLEXITY_FEE = "complexity_fee"
    WRITER_LEVEL_FEE = "writer_level_fee"
    DISCOUNT = "discount"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    TAX = "tax"

    CHOICES = [
        (SERVICE, "Service"),
        (ADDON, "Add-on"),
        (URGENCY_FEE, "Urgency fee"),
        (COMPLEXITY_FEE, "Complexity fee"),
        (WRITER_LEVEL_FEE, "Writer level fee"),
        (DISCOUNT, "Discount"),
        (MANUAL_ADJUSTMENT, "Manual adjustment"),
        (TAX, "Tax"),
    ]


class SpecialOrderQuoteEventType:
    """
    Events used for quote tracking and analytics.
    """

    CREATED = "created"
    UPDATED = "updated"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REMINDER_SENT = "reminder_sent"

    CHOICES = [
        (CREATED, "Created"),
        (UPDATED, "Updated"),
        (SENT, "Sent"),
        (VIEWED, "Viewed"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
        (REMINDER_SENT, "Reminder sent"),
    ]
from __future__ import annotations


class DiscountType:
    """
    Supported discount calculation types.
    """

    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"

    CHOICES = (
        (PERCENTAGE, "Percentage"),
        (FIXED_AMOUNT, "Fixed amount"),
    )


class DiscountOrigin:
    """
    Source of a discount.
    """

    MANUAL = "manual"
    FIRST_ORDER = "first_order"
    HOLIDAY = "holiday"
    LOYALTY = "loyalty"
    REFERRAL = "referral"
    CAMPAIGN = "campaign"
    SPEND_TIER = "spend_tier"
    SYSTEM = "system"

    CHOICES = (
        (MANUAL, "Manual"),
        (FIRST_ORDER, "First order"),
        (HOLIDAY, "Holiday"),
        (LOYALTY, "Loyalty"),
        (REFERRAL, "Referral"),
        (CAMPAIGN, "Campaign"),
        (SPEND_TIER, "Spend tier"),
        (SYSTEM, "System"),
    )

class DiscountStatus:
    """
    Derived discount status values used by selectors and APIs.
    """

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    EXPIRED = "expired"
    EXHAUSTED = "exhausted"
    ARCHIVED = "archived"
    DISABLED = "disabled"


class PayableType:
    """
    Supported payable objects that may consume discounts.
    """

    ORDER = "order"
    SPECIAL_ORDER = "special_order"
    CLASS_ORDER = "class_order"

    CHOICES = (
        (ORDER, "Order"),
        (SPECIAL_ORDER, "Special order"),
        (CLASS_ORDER, "Class order"),
    )


class DiscountConversionEvent:
    """
    Discount funnel event names.
    """

    VIEWED = "viewed"
    PREVIEWED = "previewed"
    APPLIED = "applied"
    REJECTED = "rejected"
    REMOVED = "removed"
    PAID = "paid"
    EXPIRED_AT_CHECKOUT = "expired_at_checkout"

    CHOICES = (
        (VIEWED, "Viewed"),
        (PREVIEWED, "Previewed"),
        (APPLIED, "Applied"),
        (REJECTED, "Rejected"),
        (REMOVED, "Removed"),
        (PAID, "Paid"),
        (EXPIRED_AT_CHECKOUT, "Expired at checkout"),
    )
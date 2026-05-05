from __future__ import annotations


class DiscountType:
    """
    How a discount value is interpreted.
    """

    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    MANUAL = "manual"

    CHOICES = [
        (PERCENTAGE, "Percentage"),
        (FIXED_AMOUNT, "Fixed amount"),
        (MANUAL, "Manual"),
    ]


class DiscountStatus:
    """
    Lifecycle of a discount rule or application.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    USED = "used"
    CANCELLED = "cancelled"

    CHOICES = [
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
        (EXPIRED, "Expired"),
        (USED, "Used"),
        (CANCELLED, "Cancelled"),
    ]


class DiscountScope:
    """
    Where a discount can be applied.
    """

    FIXED_SPECIAL_ORDER = "fixed_special_order"
    QUOTED_SPECIAL_ORDER = "quoted_special_order"
    ALL_SPECIAL_ORDERS = "all_special_orders"

    CHOICES = [
        (FIXED_SPECIAL_ORDER, "Fixed special order"),
        (QUOTED_SPECIAL_ORDER, "Quoted special order"),
        (ALL_SPECIAL_ORDERS, "All special orders"),
    ]
from django.db import models


class EventType(models.TextChoices):
    ORDER_EARNING         = "order_earning",          "Order earning"
    CLASS_EARNING         = "class_earning",          "Class earning"
    SPECIAL_ORDER_EARNING = "special_order_earning",  "Special order earning"
    TIP                   = "tip",                    "Tip"
    BONUS                 = "bonus",                  "Bonus"
    FINE                  = "fine",                   "Fine"
    ADJUSTMENT            = "adjustment",             "Adjustment"
    REVERSAL              = "reversal",               "Reversal"
    ADVANCE               = "advance",                "Advance"
    ADVANCE_REPAYMENT     = "advance_repayment",      "Advance repayment"
    DISPUTE               = "dispute",                "Dispute"
    CANCELLATION = "cancellation", "Cancellation"


class EventStatus(models.TextChoices):
    PENDING   = "pending",   "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    HELD      = "held",      "Held"
    CANCELLED = "cancelled", "Cancelled"
    PAID      = "paid",      "Paid"


class WindowStatus(models.TextChoices):
    OPEN       = "open",       "Open"
    CLOSED     = "closed",     "Closed"
    PROCESSING = "processing", "Processing"
    DONE       = "done",       "Done"


class CycleType(models.TextChoices):
    BIWEEKLY = "biweekly", "Bi-weekly"
    MONTHLY  = "monthly",  "Monthly"


class PayoutItemStatus(models.TextChoices):
    PENDING   = "pending",   "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PAID      = "paid",      "Paid"
    HELD      = "held",      "Held"


class CycleChangeStatus(models.TextChoices):
    PENDING  = "pending",  "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


# Positive event types — earnings
EARNING_TYPES = {
    EventType.ORDER_EARNING,
    EventType.CLASS_EARNING,
    EventType.SPECIAL_ORDER_EARNING,
    EventType.TIP,
    EventType.BONUS,
    EventType.ADVANCE,
}

# Negative event types — deductions
DEDUCTION_TYPES = {
    EventType.FINE,
    EventType.REVERSAL,
    EventType.ADVANCE_REPAYMENT,
    EventType.DISPUTE,
    EventType.CANCELLATION,
}
from __future__ import annotations


class SpecialOrderAnalyticsEventType:
    """
    Events used for special order analytics.
    """

    REQUEST_CREATED = "request_created"
    QUOTE_CREATED = "quote_created"
    QUOTE_SENT = "quote_sent"
    QUOTE_VIEWED = "quote_viewed"
    QUOTE_ACCEPTED = "quote_accepted"
    QUOTE_REJECTED = "quote_rejected"
    QUOTE_EXPIRED = "quote_expired"
    PAYMENT_STARTED = "payment_started"
    PAYMENT_APPLIED = "payment_applied"
    ORDER_READY_FOR_STAFFING = "order_ready_for_staffing"
    ORDER_COMPLETED = "order_completed"
    REFUND_REQUESTED = "refund_requested"
    REFUND_COMPLETED = "refund_completed"

    CHOICES = [
        (REQUEST_CREATED, "Request created"),
        (QUOTE_CREATED, "Quote created"),
        (QUOTE_SENT, "Quote sent"),
        (QUOTE_VIEWED, "Quote viewed"),
        (QUOTE_ACCEPTED, "Quote accepted"),
        (QUOTE_REJECTED, "Quote rejected"),
        (QUOTE_EXPIRED, "Quote expired"),
        (PAYMENT_STARTED, "Payment started"),
        (PAYMENT_APPLIED, "Payment applied"),
        (ORDER_READY_FOR_STAFFING, "Order ready for staffing"),
        (ORDER_COMPLETED, "Order completed"),
        (REFUND_REQUESTED, "Refund requested"),
        (REFUND_COMPLETED, "Refund completed"),
    ]


class SpecialOrderConversionStage:
    """
    Funnel stages for reporting.
    """

    INQUIRY = "inquiry"
    QUOTE_SENT = "quote_sent"
    QUOTE_ACCEPTED = "quote_accepted"
    PAYMENT_STARTED = "payment_started"
    FUNDED = "funded"
    COMPLETED = "completed"

    CHOICES = [
        (INQUIRY, "Inquiry"),
        (QUOTE_SENT, "Quote sent"),
        (QUOTE_ACCEPTED, "Quote accepted"),
        (PAYMENT_STARTED, "Payment started"),
        (FUNDED, "Funded"),
        (COMPLETED, "Completed"),
    ]
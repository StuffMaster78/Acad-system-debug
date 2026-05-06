class AuditEventTaxonomy:
    """
    Single source of truth for event naming conventions.
    Prevents drift across apps.
    """

    # -------------------
    # ORDER DOMAIN
    # -------------------
    ORDER_CREATED = "order.created"
    ORDER_UPDATED = "order.updated"
    ORDER_STATUS_CHANGED = "order.status_changed"
    ORDER_DELETED = "order.deleted"

    # -------------------
    # PAYMENT DOMAIN
    # -------------------
    PAYMENT_INITIATED = "payment.initiated"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"

    # -------------------
    # MESSAGES DOMAIN
    # -------------------
    MESSAGE_SENT = "message.sent"
    MESSAGE_EDITED = "message.edited"
    MESSAGE_DELETED = "message.deleted"

    # -------------------
    # SPECIAL ORDERS
    # -------------------
    SPECIAL_ORDER_CREATED = "special_order.created"
    SPECIAL_ORDER_SENSITIVE_ACCESSED = "special_order.sensitive_accessed"

    # -------------------
    # SYSTEM EVENTS
    # -------------------
    SYSTEM_ERROR = "system.error"
    SYSTEM_RETRY = "system.retry"
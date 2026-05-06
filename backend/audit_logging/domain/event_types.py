class AuditActions:
    # Orders
    ORDER_CREATED = "order.created"
    ORDER_UPDATED = "order.updated"
    ORDER_STATUS_CHANGED = "order.status_changed"

    # Special Orders (sensitive system)
    SPECIAL_ORDER_CREATED = "special_order.created"
    SPECIAL_ORDER_VIEWED = "special_order.viewed"
    SPECIAL_ORDER_SENSITIVE_ACCESSED = "special_order.sensitive_accessed"

    # Communications
    MESSAGE_SENT = "message.sent"
    MESSAGE_EDITED = "message.edited"

    # Auth
    PERMISSION_GRANTED = "auth.permission_granted"
    PERMISSION_REVOKED = "auth.permission_revoked"

    # System
    SYSTEM_EVENT = "system.event"
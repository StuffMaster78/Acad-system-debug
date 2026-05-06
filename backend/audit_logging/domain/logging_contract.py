class AuditLoggingContract:
    """
    System-wide rules for what is allowed into audit logging.

    This is NOT business logic.
    This is a logging consistency contract.
    """

    # -------------------------
    # REQUIRED STRUCTURE RULE
    # -------------------------
    REQUIRED_FIELDS = [
        "action",
        "actor_id",
        "object_type",
        "object_id",
        "timestamp",
    ]

    # -------------------------
    # CORE EVENT DOMAINS
    # -------------------------
    DOMAIN_PREFIXES = {
        "order": "order.",
        "special_order": "special_order.",
        "message": "message.",
        "auth": "auth.",
        "system": "system.",
    }

    # -------------------------
    # ALLOWED ACTION PATTERN RULE
    # -------------------------
    ACTION_PATTERN = "domain.entity.action"
    # Example: order.status_changed

    # -------------------------
    # HIGH SIGNAL EVENTS ONLY
    # -------------------------
    MUST_LOG = {
        "order.created",
        "order.status_changed",
        "order.updated",

        "special_order.created",
        "special_order.sensitive_accessed",

        "message.sent",
        "message.edited",

        "auth.permission_granted",
        "auth.permission_revoked",
    }

    # -------------------------
    # CONDITIONAL LOGGING RULES
    # -------------------------
    CONDITIONAL_LOGGING = {
        "special_order.credentials_viewed",
        "admin.deleted_user",
        "payment.refund_processed",
    }

    # -------------------------
    # FORBIDDEN (NOISE CONTROL)
    # -------------------------
    FORBIDDEN = {
        "page.viewed",
        "button.clicked",
        "ui.opened",
        "serializer.validated",
        "retry.loop",
        "heartbeat",
    }

    # -------------------------
    # METADATA LIMIT RULE
    # -------------------------
    MAX_METADATA_KEYS = 10

    MAX_METADATA_DEPTH = 2

    # -------------------------
    # SENSITIVITY RULE
    # -------------------------
    SENSITIVE_ACTIONS = {
        "special_order.sensitive_accessed",
        "auth.permission_granted",
        "auth.permission_revoked",
    }
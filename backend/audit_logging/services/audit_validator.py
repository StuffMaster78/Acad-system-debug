from audit_logging.domain.logging_contract import AuditLoggingContract


class AuditValidator:
    """
    Ensures only valid audit events enter the system.

    Rules:
    - Fail fast (raise exceptions)
    - No silent drops
    """
    
    @staticmethod
    def validate(action: str, metadata: dict | None = None) -> None:
        metadata = metadata or {}

        # -------------------------
        # Type safety
        # -------------------------
        if not isinstance(action, str) or not action:
            raise ValueError("Audit action must be a non-empty string")

        if len(action) > 100:
            raise ValueError("Audit action exceeds max length (100)")

        # -------------------------
        # Naming convention
        # -------------------------
        if "." not in action:
            raise ValueError(f"Invalid audit action format: {action}")

        # -------------------------
        # Forbidden actions
        # -------------------------
        if action in AuditLoggingContract.FORBIDDEN:
            raise ValueError(f"Forbidden audit action: {action}")

        # -------------------------
        # Metadata validation
        # -------------------------
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")

        if len(metadata.keys()) > AuditLoggingContract.MAX_METADATA_KEYS:
            raise ValueError("Metadata too large for audit logging")
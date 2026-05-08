from audit_logging.domain.logging_contract import AuditLoggingContract


class AuditValidator:
    """
    Ensures only valid audit events enter the system.

    Rule:
    - fail fast
    - no silent drops
    - no side effects
    """

    @staticmethod
    def validate(action: str, metadata: dict | None = None) -> None:

        metadata = metadata or {}

        # -------------------------
        # Action validation
        # -------------------------
        if not isinstance(action, str) or not action.strip():
            raise ValueError("Audit action must be a non-empty string")

        if len(action) > 100:
            raise ValueError("Audit action exceeds max length (100)")

        # strict naming convention (current system rule)
        if "." not in action:
            raise ValueError(f"Invalid audit action format: {action}")

        if action in AuditLoggingContract.FORBIDDEN:
            raise ValueError(f"Forbidden audit action: {action}")

        # -------------------------
        # Metadata validation
        # -------------------------
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")

        if len(metadata) > AuditLoggingContract.MAX_METADATA_KEYS:
            raise ValueError("Metadata too large for audit logging")
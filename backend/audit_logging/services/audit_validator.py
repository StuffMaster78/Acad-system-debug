from audit_logging.domain.logging_contract import AuditLoggingContract


class AuditValidator:
    """
    Ensures only valid audit events enter the system.
    """

    @staticmethod
    def validate(action: str, metadata: dict | None = None) -> bool:
        metadata = metadata or {}

        # -------------------------
        # Block forbidden noise
        # -------------------------
        if action in AuditLoggingContract.FORBIDDEN:
            return False

        # -------------------------
        # Enforce metadata size limit
        # -------------------------
        if len(metadata.keys()) > AuditLoggingContract.MAX_METADATA_KEYS:
            raise ValueError("Metadata too large for audit logging")

        # -------------------------
        # Enforce naming convention
        # -------------------------
        if "." not in action:
            raise ValueError(f"Invalid action format: {action}")
        

        if not action or not isinstance(action, str):
            return False

        if len(action) > 100:
            return False

        if metadata is None:
            return True

        if not isinstance(metadata, dict):
            return False

        return True
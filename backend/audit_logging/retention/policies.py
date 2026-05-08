from dataclasses import dataclass


@dataclass(frozen=True)
class AuditRetentionPolicy:

    days: int

    archive_before_delete: bool = True
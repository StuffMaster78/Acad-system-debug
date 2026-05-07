from abc import ABC, abstractmethod
from audit_logging.models.audit_event import AuditEvent


class BaseProcessor(ABC):
    """
    Contract for all audit processors.

    Rule:
    - processors must NEVER mutate domain state
    - processors must be idempotent
    """

    @abstractmethod
    def process(self, event: AuditEvent) -> None:
        raise NotImplementedError
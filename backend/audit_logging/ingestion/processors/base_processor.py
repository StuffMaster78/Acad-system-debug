from abc import ABC, abstractmethod
import logging
from audit_logging.models.audit_event import AuditEvent

logger = logging.getLogger("audit")


class BaseProcessor(ABC):
    """
    Contract for audit processors.

    Rules:
    - MUST be idempotent
    - MUST NOT mutate AuditEvent
    - MUST NOT raise exceptions upstream
    """

    @abstractmethod
    def process(self, event: AuditEvent) -> None:
        raise NotImplementedError

    def safe_process(self, event: AuditEvent) -> None:
        """
        Wrapper for safe execution.
        """
        try:
            self.process(event)
        except Exception as exc:
            logger.exception(
                "Processor failed",
                extra={
                    "event_id": event.id,
                    "processor": self.__class__.__name__,
                    "error": str(exc),
                },
            )
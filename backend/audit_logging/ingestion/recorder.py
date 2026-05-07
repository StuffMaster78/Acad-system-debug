import logging
from typing import Iterable

from audit_logging.models.audit_event import AuditEvent
from audit_logging.ingestion.processors import get_default_processors

logger = logging.getLogger("audit")


class AuditRecorder:
    """
    Central ingestion orchestrator.

    Responsibilities:
    - dispatch event to processors
    - ensure safe execution isolation
    - never raise into domain layer
    """

    _processors = None

    @classmethod
    def ingest(cls, event: AuditEvent) -> AuditEvent:
        """
        Entry point for pipeline processing.
        """

        processors = cls._get_processors()

        for processor in processors:
            try:
                processor.process(event)

            except Exception as exc:
                # IMPORTANT:
                # ingestion must never break request flow
                logger.exception(
                    "Audit processor failed",
                    extra={
                        "event_id": event.event_id,
                        "processor": processor.__class__.__name__,
                        "error": str(exc),
                    },
                )

                # optional: send to DLQ hook later

        return event

    @classmethod
    def _get_processors(cls) -> Iterable:
        """
        Lazy-load processor registry.
        """

        if cls._processors is None:
            cls._processors = get_default_processors()

        return cls._processors
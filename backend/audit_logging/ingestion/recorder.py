import logging
from typing import Iterable, Protocol

from audit_logging.models.audit_event import AuditEvent
from audit_logging.ingestion.processors import get_default_processors

logger = logging.getLogger("audit")


# --------------------------------------------------
# Processor contract (STRICT)
# --------------------------------------------------

class AuditProcessor(Protocol):
    def process(self, event: AuditEvent) -> None:
        ...


# --------------------------------------------------
# Recorder
# --------------------------------------------------

class AuditRecorder:
    """
    Central ingestion orchestrator.

    Responsibilities:
    - dispatch event to processors
    - isolate failures
    - never break request flow
    """

    _processors: list[AuditProcessor] | None = None

    # -------------------------
    # public entrypoint
    # -------------------------

    @classmethod
    def ingest(cls, event: AuditEvent) -> AuditEvent:
        processors = cls._get_processors()

        for processor in processors:
            try:
                processor.process(event)

            except Exception as exc:
                logger.exception(
                    "Audit processor failed",
                    extra={
                        "event_id": event.id,
                        "processor": getattr(processor, "__class__", type(processor)).__name__,
                        "error": str(exc),
                    },
                )

                # future resilience hook
                # send_to_dlq(event, processor, exc)
                # FUTURE HOOK (important)
                # AuditFailureCapture.capture(event, exc)

        return event

    # -------------------------
    # processor loading
    # -------------------------

    @classmethod
    def _get_processors(cls) -> list[AuditProcessor]:
        if cls._processors is None:
            raw = get_default_processors()

            validated = []

            # defensive normalization
            for p in raw:
                process_fn = getattr(p, "process", None)

                if callable(process_fn):
                    validated.append(p)
                else:
                    logger.warning(
                        "Invalid audit processor skipped",
                        extra={"processor": str(p)},
                    )

            cls._processors = validated


        return cls._processors
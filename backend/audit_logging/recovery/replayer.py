import logging

from audit_logging.recovery.dlq_store import DeadLetterQueueStore
from audit_logging.tasks import process_audit_event_task

logger = logging.getLogger("audit")


class AuditDLQReplayer:

    @staticmethod
    def replay_batch(limit: int = 50):

        items = DeadLetterQueueStore.fetch_batch(limit=limit)

        for item in items:

            event_id = (item.event_payload or {}).get("audit_event_id")

            if not event_id:
                logger.warning(
                    "DLQ_REPLAY_SKIP_MISSING_AUDIT_EVENT_ID",
                    extra={"dlq_id": item.id},
                )
                continue

            process_audit_event_task.delay(str(event_id)) #type: ignore

    @staticmethod
    def replay_single(item):

        event_id = (item.event_payload or {}).get("audit_event_id")

        if not event_id:
            logger.warning(
                "DLQ_REPLAY_SINGLE_SKIP_MISSING_AUDIT_EVENT_ID",
                extra={"dlq_id": item.id},
            )
            return

        process_audit_event_task.delay(str(event_id)) #type: ignore
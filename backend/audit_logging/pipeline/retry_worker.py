import logging
from audit_logging.storage.models import AuditEvent
from audit_logging.storage.dlq_store import DeadLetterQueueStore

logger = logging.getLogger("audit_logging")


class AuditRetryWorker:

    def run_once(self):
        batch = DeadLetterQueueStore.fetch_batch()

        for item in batch:
            event_data = item.event_payload

            try:
                event = AuditEvent(
                    event_id=event_data["event_id"],
                    actor_id=event_data.get("actor_id"),
                    action=event_data["action"],
                    object_type=event_data.get("object_type"),
                    object_id=event_data.get("object_id"),
                    metadata=event_data.get("metadata", {}),
                    is_sensitive=event_data.get("is_sensitive", False),
                )

                event.save()

                DeadLetterQueueStore.mark_resolved(item)

            except Exception as e:
                logger.error(
                    "AUDIT_RETRY_FAILED",
                    extra={
                        "event_id": event_data.get("event_id"),
                        "error": str(e),
                    },
                )

                DeadLetterQueueStore.increment_retry(item)

    def run_forever(self, interval_seconds=30):
        import time

        while True:
            self.run_once()
            time.sleep(interval_seconds)
import logging

logger = logging.getLogger("event_system")


class EventMetrics:
    @staticmethod
    def record_processed(event_type: str):
        logger.info("event_processed", extra={"event_type": event_type})

    @staticmethod
    def record_failed(event_type: str, error: str):
        logger.error(
            "event_failed",
            extra={"event_type": event_type, "error": error},
        )

    @staticmethod
    def record_dead_letter(event_type: str):
        logger.critical(
            "event_dead_letter",
            extra={"event_type": event_type},
        )
from django.core.cache import cache


class EventExecutionRecordService:
    """
    Prevents duplicate side effects during replay + retries.
    """

    PREFIX = "event_execution:"

    @classmethod
    def has_run(cls, event_id: str) -> bool:
        return cache.get(cls.PREFIX + event_id) is not None

    @classmethod
    def mark_run(cls, event_id: str) -> None:
        cache.set(cls.PREFIX + event_id, True, timeout=86400 * 7)

    @classmethod
    def clear(cls, event_id: str) -> None:
        cache.delete(cls.PREFIX + event_id)
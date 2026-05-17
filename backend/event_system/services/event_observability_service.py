from django.core.cache import cache


class EventObservabilityService:
    """
    Lightweight metrics + tracing layer.
    """

    PREFIX = "event_obs:"

    @classmethod
    def record_latency(cls, event_type: str, duration_ms: float) -> None:
        key = f"{cls.PREFIX}latency:{event_type}"

        cache.set(key, duration_ms)

    @classmethod
    def increment_failure(cls, event_type: str) -> None:
        key = f"{cls.PREFIX}failures:{event_type}"
        cache.set(key, (cache.get(key) or 0) + 1)

    @classmethod
    def increment_success(cls, event_type: str) -> None:
        key = f"{cls.PREFIX}success:{event_type}"
        cache.set(key, (cache.get(key) or 0) + 1)
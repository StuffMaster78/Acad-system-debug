import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)


def check_redis_health() -> bool:
    """
    Check if Redis is available and responding.

    Returns:
        bool: True if Redis is healthy, False otherwise.
    """
    redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

    try:
        client = redis.Redis.from_url(redis_url)
        healthy = client.ping()
        if healthy:
            logger.debug("Redis health check passed ✅")
        return healthy
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
    return False
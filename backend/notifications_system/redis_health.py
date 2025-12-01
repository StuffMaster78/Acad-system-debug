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
    # Allow disabling strict Redis checks in non-critical environments
    if getattr(settings, "NOTIFICATIONS_REDIS_HEALTH_CHECK_ENABLED", True) is False:
        logger.warning("Redis health check is disabled via NOTIFICATIONS_REDIS_HEALTH_CHECK_ENABLED.")
        return True

    redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

    try:
        # Parse URL to handle password correctly
        from urllib.parse import urlparse
        parsed = urlparse(redis_url)
        
        # Extract password from URL if present
        password = parsed.password if parsed.password else None
        
        # Build connection parameters
        connection_params = {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 6379,
            'db': int(parsed.path.lstrip('/')) if parsed.path else 0,
            'decode_responses': False,
        }
        
        # Add password if present
        if password:
            connection_params['password'] = password
        
        # Try connecting with explicit parameters first
        try:
            client = redis.Redis(**connection_params, socket_connect_timeout=2, socket_timeout=2)
            healthy = client.ping()
            if healthy:
                logger.debug("Redis health check passed ✅")
            return healthy
        except Exception:
            # Fallback to from_url if explicit params fail
            client = redis.Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
            healthy = client.ping()
            if healthy:
                logger.debug("Redis health check passed ✅")
            return healthy
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during Redis health check: {e}")
    return False
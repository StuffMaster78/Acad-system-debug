import logging
import redis
import socket
import time
from django.conf import settings

logger = logging.getLogger(__name__)


def check_redis_health() -> bool:
    """
    Check if Redis is available and responding.
    Includes retry logic for DNS resolution issues in Docker environments.

    Returns:
        bool: True if Redis is healthy, False otherwise.
    """
    # Allow disabling strict Redis checks in non-critical environments
    if getattr(settings, "NOTIFICATIONS_REDIS_HEALTH_CHECK_ENABLED", True) is False:
        logger.warning("Redis health check is disabled via NOTIFICATIONS_REDIS_HEALTH_CHECK_ENABLED.")
        return True

    redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
    
    # In development/Docker, be more lenient with DNS resolution errors
    is_debug = getattr(settings, "DEBUG", False)
    max_retries = 3 if is_debug else 1
    retry_delay = 1.0  # seconds

    for attempt in range(max_retries):
        try:
            # Parse URL to handle password correctly
            from urllib.parse import urlparse
            parsed = urlparse(redis_url)
            
            hostname = parsed.hostname or 'localhost'
            port = parsed.port or 6379
            
            # First, try to resolve the hostname (helps with DNS issues)
            try:
                socket.gethostbyname(hostname)
            except socket.gaierror as dns_error:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Redis DNS resolution failed for {hostname} (attempt {attempt + 1}/{max_retries}): {dns_error}. "
                        f"Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Redis DNS resolution failed for {hostname}: {dns_error}")
                    if is_debug:
                        logger.warning("Redis DNS error in DEBUG mode - this may be non-fatal if Redis starts later.")
                    return False
            
            # Extract password from URL if present
            password = parsed.password if parsed.password else None
            
            # Build connection parameters
            connection_params = {
                'host': hostname,
                'port': port,
                'db': int(parsed.path.lstrip('/')) if parsed.path else 0,
                'decode_responses': False,
                'socket_connect_timeout': 3,  # Increased timeout
                'socket_timeout': 3,
            }
            
            # Add password if present
            if password:
                connection_params['password'] = password
            
            # Try connecting with explicit parameters first
            try:
                client = redis.Redis(**connection_params)
                healthy = client.ping()
                if healthy:
                    logger.debug("Redis health check passed ✅")
                return healthy
            except (redis.ConnectionError, redis.TimeoutError) as conn_error:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Redis connection failed (attempt {attempt + 1}/{max_retries}): {conn_error}. "
                        f"Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    continue
                else:
                    # Fallback to from_url if explicit params fail
                    try:
                        client = redis.Redis.from_url(redis_url, socket_connect_timeout=3, socket_timeout=3)
                        healthy = client.ping()
                        if healthy:
                            logger.debug("Redis health check passed ✅ (via from_url)")
                        return healthy
                    except Exception as fallback_error:
                        logger.error(f"Redis connection error (fallback also failed): {fallback_error}")
                        return False
        except redis.RedisError as e:
            logger.error(f"Redis error: {e}")
            return False
        except Exception as e:
            error_msg = str(e)
            # Check if it's a DNS/network error
            if "Name or service not known" in error_msg or "Errno -2" in error_msg:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Redis DNS/network error (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Redis DNS/network error after {max_retries} attempts: {e}")
                    if is_debug:
                        logger.warning("Redis DNS error in DEBUG mode - this may be non-fatal if Redis starts later.")
                    return False
            else:
                logger.error(f"Unexpected error during Redis health check: {e}")
                return False
    
    return False
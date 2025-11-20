from django.core.cache import cache
from users.models import User
import hashlib
import random
import string
import logging


logger = logging.getLogger(__name__)

def is_rate_limited(user, action, max_attempts=5, window=300):
    """
    Check if a user has exceeded rate limits for a given action.
    
    max_attempts: Maximum number of attempts allowed.
    window: Time window (in seconds) within which attempts are counted.
    """
    cache_key = f"{user.id}_{action}_attempts"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= max_attempts:
        logger.warning(f"User {user.id} exceeded max attempts for {action}.")
        return True
    
    cache.set(cache_key, attempts + 1, timeout=window)
    return False


# Rate Limiting with Device/IP Recognition
def is_device_rate_limited(user, action, ip, device_id, max_attempts=5, window=300):
    """
    Rate limit based on device/IP.
    """
    cache_key = f"{user.id}_{action}_{ip}_{device_id}_attempts"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= max_attempts:
        logger.warning(f"Device rate-limited for user {user.id} at IP {ip}.")
        return True
    
    cache.set(cache_key, attempts + 1, timeout=window)
    return False


def generate_backup_codes(user):
    """
    Generates and stores backup codes for MFA recovery.
    """
    codes = [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(5)]
    hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in codes]
    user.backup_codes = hashed_codes
    user.save()
    return codes

def use_backup_code(user, code):
    """
    Verify and remove a used backup code.
    """
    hashed_code = hashlib.sha256(code.encode()).hexdigest()
    if hashed_code in user.backup_codes:
        user.backup_codes.remove(hashed_code)
        user.save()
        return True
    logger.warning(f"Invalid backup code for user {user.id}.")
    return False
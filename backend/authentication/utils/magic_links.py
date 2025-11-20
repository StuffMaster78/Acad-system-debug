from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from authentication.models.magic_links import MagicLink
import logging

logger = logging.getLogger(__name__)

def generate_magic_link(user, expires_in=60):
    """
    Generate a unique magic link token and store it.
    
    expires_in: Time in minutes until the magic link expires (default is 60 minutes).
    """
    expiration_time = timezone.now() + timedelta(minutes=expires_in)
    token = get_random_string(64)
    MagicLink.objects.create(
        user=user,
        token=token,
        expiration_time=expiration_time
    )
    
    return token

def verify_magic_link(user, token):
    """
    Verify magic Link and clean up.
    """
    try:
        magic_link = MagicLink.objects.get(user=user, token=token)
        if magic_link.expiration_time > timezone.now():
            magic_link.delete()  # Clean up after use
            return True
        else:
            magic_link.delete()  # Clean up expired magic link
            logger.warning(f"Magic link expired for user {user.id}.")
            return False
    except MagicLink.DoesNotExist:
        logger.warning(f"Invalid magic link for user {user.id}.")
        return False
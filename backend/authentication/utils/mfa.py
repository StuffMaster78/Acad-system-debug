import pyotp
from django.core.cache import cache

def get_mfa_session_by_token(mfa_token):
    """
    Retrieve the MFA session data from cache using the token.
    Returns None if no session is found or expired.
    """
    session_data = cache.get(f"mfa_session:{mfa_token}")
    if not session_data:
        return None

    # Usually session_data might include user_id, expiry, etc.
    # Example: {'user_id': 123, 'expiry': datetime, ...}

    # You can fetch User object if you want:
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(pk=session_data['user_id'])
        session_data['user'] = user
    except User.DoesNotExist:
        return None

    return session_data


def verify_mfa_code(user, submitted_code):
    """
    Verify the MFA TOTP code for a given user.

    Args:
        user: Django User instance with mfa_secret attribute.
        submitted_code (str): The code user entered.

    Returns:
        bool: True if code is valid, False otherwise.
    """
    if not hasattr(user, 'mfa_secret') or not user.mfa_secret:
        # User doesn't have MFA enabled
        return False

    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(submitted_code, valid_window=1)  # allows 1 step clock drift (~30s)

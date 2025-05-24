import jwt
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from users.models import User
from django.core.cache import cache

logger = logging.getLogger(__name__)
BLACKLISTED_TOKEN_PREFIX = "bljwt"



def blacklist_token(token):
    """
    Store token in cache to mark it as used/invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        exp = payload.get("exp")
        ttl = exp - int(datetime.utcnow().timestamp())
        cache.set(f"bl_{token}", True, timeout=ttl)
    except Exception as e:
        logger.warning(f"Token invalidation failed: {e}")

def is_token_blacklisted(token):
    return cache.get(f"bl_{token}") is True

def invalidate_token(jti, ttl=None):
    """
    Store the token ID (jti) in the cache to mark it as invalid.
    """
    key = f"{BLACKLISTED_TOKEN_PREFIX}:{jti}"
    cache.set(key, True, timeout=ttl or settings.JWT_TOKEN_TTL)

def is_token_invalid(jti):
    """
    Check if the token ID (jti) is blacklisted.
    """
    key = f"{BLACKLISTED_TOKEN_PREFIX}:{jti}"
    return cache.get(key) is not None


def get_tokens_for_user(user):
    """
    Generate refresh and access tokens for a given user using SimpleJWT.

    Args:
        user (User): Django User instance.

    Returns:
        dict: Dictionary with 'refresh' and 'access' tokens.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def encode_verification_token(user, expiry_minutes=30, token_type="verification", extra_payload=None):
    """
    Encode a custom JWT token for verification purposes.

    Args:
        user (User): Django User instance.
        expiry_minutes (int): Token expiration time in minutes.
        token_type (str): Type of token for tracking purpose.

    Returns:
        str: Encoded JWT token.
    """
    expiration = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    payload = {
        "user_id": user.id,
        "exp": expiration,
        "iat": datetime.utcnow(),
        "type": token_type
    }

    if extra_payload:
        payload.update(extra_payload)

    try:
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token
    except Exception as e:
        logger.error(f"Token encoding error [{token_type}]: {str(e)}")
        raise Exception("Failed to encode verification token.")


def decode_verification_token(token, expected_type=None):
    """
    Decode a JWT verification token and optionally validate its type.

    Args:
        token (str): Encoded JWT token.
        expected_type (str): Expected type of token (default is 'verification').

    Returns:
        User: The user instance associated with the token.

    Raises:
        AuthenticationFailed: If token is expired, invalid, or user doesn't exist.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        if expected_type and payload.get("type") != expected_type:
            raise AuthenticationFailed("Token type mismatch.")
        
        jti = payload.get("jti")
        if is_token_invalid(jti):
            raise AuthenticationFailed("Token has already been used.")

        user_id = payload["user_id"]
        user = User.objects.get(id=user_id)
        return user

    except jwt.ExpiredSignatureError:
        logger.warning(f"Token expired: {token}")
        raise AuthenticationFailed("Verification token expired.")

    except jwt.InvalidTokenError:
        logger.warning(f"Invalid token: {token}")
        raise AuthenticationFailed("Invalid token.")

    except ObjectDoesNotExist:
        logger.warning(f"User not found for token: {token}")
        raise AuthenticationFailed("User not found.")
    

def encode_password_reset_token(user, expiry_minutes=30):
    """
    Generate a JWT token for password reset.
    
    Args:
        user (User): The user instance.
        expiry_minutes (int): Token validity in minutes.

    Returns:
        str: Encoded JWT token.
    """
    expiration = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    payload = {
        'user_id': user.id,
        'exp': expiration,
        'iat': datetime.utcnow(),
        'type': 'password_reset'
    }

    try:
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        logger.error(f"Error encoding password reset token: {str(e)}")
        raise Exception("Token creation failed")

    return token if isinstance(token, str) else token.decode('utf-8')


def decode_password_reset_token(token):
    """
    Decode a JWT token and validate it for password reset use.
    
    Args:
        token (str): The JWT token string.

    Returns:
        User: The user instance from token.

    Raises:
        AuthenticationFailed: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )

        if payload.get('type') != 'password_reset':
            raise AuthenticationFailed('Invalid token type.')

        user = User.objects.get(id=payload['user_id'])
        return user

    except jwt.ExpiredSignatureError:
        logger.warning(f"Password reset token expired: {token}")
        raise AuthenticationFailed('Token expired.')
    except jwt.InvalidTokenError:
        logger.warning(f"Invalid password reset token: {token}")
        raise AuthenticationFailed('Invalid token.')
    except User.DoesNotExist:
        logger.warning(f"User not found for token: {token}")
        raise AuthenticationFailed('User not found.')
    
def encode_magic_link_token(user, expiry_minutes=10):
    """
    Generate a JWT token for magic link login.

    Args:
        user (User): The user instance.
        expiry_minutes (int): Token validity in minutes.

    Returns:
        str: Encoded JWT token.
    """
    expiration = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    payload = {
        'user_id': user.id,
        'exp': expiration,
        'iat': datetime.utcnow(),
        'type': 'magic_link'
    }

    try:
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    except Exception as e:
        logger.error(f"Error encoding magic link token: {str(e)}")
        raise Exception("Token creation failed")

    return token if isinstance(token, str) else token.decode('utf-8')


def decode_magic_link_token(token):
    """
    Decode a JWT token and validate it for magic link login.

    Args:
        token (str): The JWT token string.

    Returns:
        User: The user instance from token.

    Raises:
        AuthenticationFailed: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        if payload.get('type') != 'magic_link':
            raise AuthenticationFailed('Invalid token type.')

        user_id = payload.get('user_id')
        user = User.objects.get(id=user_id)
        return user

    except jwt.ExpiredSignatureError:
        logger.warning(f"Magic link token expired: {token}")
        raise AuthenticationFailed('Token expired.')
    except jwt.InvalidTokenError:
        logger.warning(f"Invalid magic link token: {token}")
        raise AuthenticationFailed('Invalid token.')
    except User.DoesNotExist:
        logger.warning(f"User not found for magic link token: {token}")
        raise AuthenticationFailed('User not found.')
    

def encode_mfa_token(user, expiry_minutes=5, challenge_type="totp"):
    """
    Generate a JWT token for MFA challenge step.

    Args:
        user (User): The user instance.
        expiry_minutes (int): Token validity in minutes.
        challenge_type (str): The type of MFA challenge (e.g., 'totp', 'webauthn').

    Returns:
        str: Encoded JWT token.
    """
    expiration = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    payload = {
        'user_id': user.id,
        'exp': expiration,
        'iat': datetime.utcnow(),
        'type': 'mfa_challenge',
        'challenge_type': challenge_type,
    }

    try:
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    except Exception as e:
        logger.error(f"Error encoding MFA token: {str(e)}")
        raise Exception("MFA token generation failed")

    return token if isinstance(token, str) else token.decode('utf-8')


def decode_mfa_token(token, expected_challenge_type=None):
    """
    Decode and validate a JWT token for MFA challenge.

    Args:
        token (str): The JWT token string.
        expected_challenge_type (str, optional): Challenge type to validate.

    Returns:
        User: The user instance associated with the MFA token.

    Raises:
        AuthenticationFailed: If token is invalid, expired, or doesn't match.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        if payload.get('type') != 'mfa_challenge':
            raise AuthenticationFailed('Invalid token type.')

        if expected_challenge_type and \
                payload.get('challenge_type') != expected_challenge_type:
            raise AuthenticationFailed('Invalid MFA challenge type.')

        user_id = payload['user_id']
        user = User.objects.get(id=user_id)
        return user

    except jwt.ExpiredSignatureError:
        logger.warning(f"MFA token expired: {token}")
        raise AuthenticationFailed('MFA token expired.')
    except jwt.InvalidTokenError:
        logger.warning(f"Invalid MFA token: {token}")
        raise AuthenticationFailed('Invalid MFA token.')
    except User.DoesNotExist:
        logger.warning(f"User not found for MFA token: {token}")
        raise AuthenticationFailed('User not found.')
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
import logging

logger = logging.getLogger(__name__)

def encode_verification_token(user, expiry_minutes=30):
    """
    Generate a JWT token for email verification or similar use.
    
    Args:
        user (User): The user instance to encode into the token.
        expiry_minutes (int): Minutes until the token expires.

    Returns:
        str: Encoded JWT token.
    """
    expiration = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    payload = {
        'user_id': user.id,
        'exp': expiration,
        'iat': datetime.utcnow(),
        'type': 'verification'
    }

    try: 
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        logger.error(f"Error encoding verification token: {str(e)}")
        raise Exception("Error encoding verification token")


    return token if isinstance(token, str) else token.decode('utf-8')

def decode_verification_token(token):
    """
    Decode the JWT token to get user data (e.g., user ID) and validate the token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        user_id = payload['user_id']
        user = User.objects.get(id=user_id)

        return user
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token expired: {token}")
        raise AuthenticationFailed('The verification token has expired.')
    except jwt.InvalidTokenError:
        logger.warning(f"Invalid token: {token}")
        raise AuthenticationFailed('Invalid token.')
    except User.DoesNotExist:
        logger.warning(f"User not found for token: {token}")
        raise AuthenticationFailed('User not found.')
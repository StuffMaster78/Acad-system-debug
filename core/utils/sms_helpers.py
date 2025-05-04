# core/utils/sms_helpers.py
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_twilio_client():
    """
    Returns a Twilio client initialized with the account SID and Auth Token
    from settings.
    """
    try:
        return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    except Exception as e:
        logger.error(f"Error initializing Twilio client: {e}")
        raise

def send_sms_notification(user, message):
    """
    Sends an SMS notification to the user using Twilio.

    :param user: The user receiving the SMS notification (must have a phone number).
    :param message: The message content to be sent.
    """
    if not user.phone_number:
        logger.warning(f"User {user.username} does not have a phone number.")
        return False  # Return false if the user doesn't have a phone number.

    try:
        client = get_twilio_client()
        
        # Send the SMS
        message_sent = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,  # Your Twilio phone number
            to=user.phone_number  # User's phone number
        )
        
        # Log the message SID for debugging
        logger.info(f"Sent SMS to {user.phone_number}: {message_sent.sid}")
        return True

    except Exception as e:
        logger.error(f"Failed to send SMS to {user.phone_number}: {e}")
        return False
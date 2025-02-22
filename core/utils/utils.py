from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

def send_email(user, subject, message):
    """
    Send an email notification.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

def send_sms(to_number, message):
    """
    Send an SMS notification using Twilio.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_number,
    )

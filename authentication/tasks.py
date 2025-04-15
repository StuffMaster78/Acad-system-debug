from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from authentication.models.otp import OTP
from authentication.models.magic_links import MagicLink


# Asynchronous task for sending email
@shared_task
def send_email_async(subject, message, sender_email, receiver_email):
    send_mail(
        subject, message, sender_email,
        [receiver_email], fail_silently=False
    )

# Cleanup Expired OTPs and Magic Links (Scheduled Cleanup Task)
@shared_task
def cleanup_expired_otp_and_magic_links():
    """
    Cleanup expired OTPs and MagicLinks from the database.
    This task can be scheduled periodically (e.g., every hour).
    """
    OTP.objects.filter(expiration_time__lt=timezone.now()).delete()
    MagicLink.objects.filter(expiration_time__lt=timezone.now()).delete()
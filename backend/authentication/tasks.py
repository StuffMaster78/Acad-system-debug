from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from authentication.models.otp import OTP
from authentication.models.magic_links import MagicLink
from django.utils.timezone import now
from authentication.models.deletion_requests import AccountDeletionRequest
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


@shared_task
def purge_expired_deletions():
    expired_requests = AccountDeletionRequest.objects.filter(
        status=AccountDeletionRequest.CONFIRMED,
        scheduled_deletion_time__lte=now()
    )
    for req in expired_requests:
        req.user.delete()
        req.delete()

@shared_task
def cleanup_expired_magic_links():
    """
    Deletes all expired magic links.
    """
    expired_links = MagicLink.objects.filter(expires_at__lt=now())
    count = expired_links.count()
    expired_links.delete()
    return f"Deleted {count} expired magic links"

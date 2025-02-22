# File: myapp/tasks.py
from celery import shared_task
from django.utils.timezone import now
from .models import Probation, SuperadminLog
from django.core.mail import send_mail
from django.conf import settings
import logging
from smtplib import SMTPException
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

@shared_task
def check_probation_expiry():
    """Checks if any probations have expired and deactivates them."""
    expired_probations = Probation.objects.filter(is_active=True, end_date__lt=now())
    count = expired_probations.count()

    for probation in expired_probations:
        probation.is_active = False
        probation.save()

        # Log action
        SuperadminLog.objects.create(
            superadmin=probation.placed_by,
            action_type="probation",
            action_details=f"Probation expired for {probation.user.username}."
        )

        # Notify user
        if probation.user.email:
            send_email_task.delay(
                subject="Probation Period Ended",
                message=f"Hello {probation.user.username},\n\nYour probation period has ended. You now have full system access.",
                recipient_list=[probation.user.email]
            )
        else:
            logger.warning(f"User {probation.user.username} has no email, skipping notification.")

    logger.info(f"Processed {count} expired probations.")
    return f"Processed {count} expired probations."


### 🔹 2️⃣ Task: Email Sending with Retry Mechanism
@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, recipient_list):
    """Retries sending emails up to 3 times if it fails."""
    try:
        if not recipient_list:
            raise ValidationError("Recipient list is empty. Email not sent.")

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,  # Fail explicitly to trigger retry
        )

        logger.info(f"Email successfully sent to {recipient_list}")

    except (SMTPException, ConnectionError) as e:
        logger.error(f"Email failed due to network issue: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds

    except Exception as e:
        logger.error(f"Email failed permanently: {e}")
        return f"Email delivery failed: {str(e)}"
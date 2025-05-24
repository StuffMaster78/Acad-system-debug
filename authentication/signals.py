from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LoginSession
from .utils_backp import get_country_and_timezone
from ipware import get_client_ip # type: ignore
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.conf import settings
from .models import DeletionRequest
import logging
from django.dispatch import Signal

auth_event = Signal()

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def track_login_data(sender, request, user, **kwargs):
    ip, _ = get_client_ip(request)
    country, timezone = get_country_and_timezone(ip)
    LoginSession.objects.create(
        user=user,
        ip_address=ip,
        country=country,
        timezone=timezone,
        user_agent=request.META.get("HTTP_USER_AGENT"),
    )



@receiver(post_save, sender=DeletionRequest)
def send_confirmation_email(sender, instance, created, **kwargs):
    if instance.status == DeletionRequest.CONFIRMED:
        # Send an email to the user confirming deletion.
        send_mail(
            'Your account deletion request has been confirmed',
            'Your account deletion request has been processed.',
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email]
        )

def log_auth_event(sender, **kwargs):
    user = kwargs.get('user')
    event = kwargs.get('event')
    ip = kwargs.get('ip')
    logger.info(f"Auth Event: {event} | User: {user} | IP: {ip}")

auth_event.connect(log_auth_event)
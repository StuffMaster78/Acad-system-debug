import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils.email_helpers import send_website_mail
from notifications_system.services.notification_service import NotificationService
from .models import Ticket, TicketLog

logger = logging.getLogger(__name__)


def _safe_send_mail(subject: str, message: str, recipient: str | None, website=None):
    try:
        if recipient:
            send_website_mail(subject, message, [recipient], website=website)
    except Exception:
        # Never break request handling due to email issues
        pass


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance: Ticket, created, **kwargs):
    """
    Ticket side effects now live in tickets.services.

    The receiver remains registered as a compatibility placeholder so older
    imports do not fail, but it no longer creates duplicate logs or sends
    duplicate notifications for service-managed actions.
    """
    return None

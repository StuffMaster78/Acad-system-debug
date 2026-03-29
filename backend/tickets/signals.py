import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications_system.services.notification_service import (
    NotificationService,
)

from .models import Ticket, TicketLog

logger = logging.getLogger(__name__)


def _safe_send_mail(subject: str, message: str, recipient: str | None):
    try:
        if recipient:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
    except Exception:
        # Never break tests due to email issues
        pass


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance: Ticket, created, **kwargs):
    """Handle ticket logs and notifications after save."""
    if created:
        TicketLog.objects.create(
            ticket=instance,
            action="Ticket created",
            performed_by=instance.created_by,
        )

        try:
            if instance.created_by and instance.website:
                NotificationService.notify(
                    event_key="ticket.created",
                    recipient=instance.created_by,
                    website=instance.website,
                    context={
                        "ticket_id": instance.id,
                        "ticket_number": f"#{instance.id}",
                        "title": instance.title,
                        "status": instance.status,
                        "website_id": instance.website_id,
                    },
                    channels=["email", "in_app"],
                    triggered_by=instance.created_by,
                    priority="normal",
                    is_broadcast=False,
                    is_critical=False,
                    is_digest=False,
                    is_silent=False,
                    digest_group=None,
                )
        except Exception as exc:
            logger.error(
                "Failed to send ticket created notification: %s",
                exc,
            )

        website_admin_email = getattr(
            instance.website,
            "default_sender_email",
            None,
        )
        _safe_send_mail(
            f"New Ticket Created: {instance.title}",
            f"A new ticket titled '{instance.title}' has been created.",
            website_admin_email,
        )
    else:
        TicketLog.objects.create(
            ticket=instance,
            action=f"Ticket updated: Status={instance.status}",
            performed_by=instance.created_by,
        )

    if getattr(instance, "assigned_to", None) and not created:
        TicketLog.objects.create(
            ticket=instance,
            action=f"Ticket assigned to {instance.assigned_to.username}",
            performed_by=instance.created_by,
        )

        try:
            NotificationService.notify(
                event_key="ticket.assigned",
                recipient=instance.assigned_to,
                website=instance.website,
                context={
                    "ticket_id": instance.id,
                    "ticket_number": f"#{instance.id}",
                    "title": instance.title,
                    "assignee_name": (
                        instance.assigned_to.get_full_name()
                        or instance.assigned_to.username
                    ),
                    "website_id": instance.website_id,
                },
                channels=["email", "in_app"],
                triggered_by=instance.created_by,
                priority="normal",
                is_broadcast=False,
                is_critical=False,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception as exc:
            logger.error(
                "Failed to send ticket assigned notification: %s",
                exc,
            )

        _safe_send_mail(
            f"Ticket Assigned: {instance.title}",
            f"You have been assigned to the ticket "
            f"'{instance.title}'.",
            getattr(instance.assigned_to, "email", None),
        )

    if getattr(instance, "is_escalated", False):
        TicketLog.objects.create(
            ticket=instance,
            action="Ticket escalated to high priority",
            performed_by=instance.created_by,
        )
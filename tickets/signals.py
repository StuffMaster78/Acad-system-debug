from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail  # Optional for email notifications
from .models import Ticket, TicketLog
from django.conf import settings


def _safe_send_mail(subject: str, message: str, recipient: str | None):
    try:
        if recipient:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
    except Exception:
        # Never break tests due to email issues
        pass


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance: Ticket, created, **kwargs):
    # Always ensure TicketLog.website is populated via model save; only set minimal fields here
    if created:
        TicketLog.objects.create(
            ticket=instance,
            action="Ticket created",
            performed_by=instance.created_by,
        )
        
        # Send notification using NotificationHelper
        try:
            from notifications_system.services.notification_helper import NotificationHelper
            NotificationHelper.notify_ticket_created(
                ticket=instance,
                creator=instance.created_by
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send ticket created notification: {e}")
        
        # Best-effort notify website admin if available (legacy)
        website_admin_email = getattr(instance.website, "default_sender_email", None)
        _safe_send_mail(
            f"New Ticket Created: {instance.title}",
            f"A new ticket titled '{instance.title}' has been created.",
            website_admin_email,
        )
    else:
        # Minimal update log; avoid spamming multiple logs from other handlers
        TicketLog.objects.create(
            ticket=instance,
            action=f"Ticket updated: Status={instance.status}",
            performed_by=instance.created_by,
        )

    # Assignment change notification
    if getattr(instance, "assigned_to", None) and not created:
        TicketLog.objects.create(
            ticket=instance,
            action=f"Ticket assigned to {instance.assigned_to.username}",
            performed_by=instance.created_by,
        )
        
        # Send notification
        try:
            from notifications_system.services.notification_helper import NotificationHelper
            NotificationHelper.send_notification(
                user=instance.assigned_to,
                event="ticket.assigned",
                payload={
                    "ticket_id": instance.id,
                    "ticket_number": f"#{instance.id}",
                    "assignee_name": instance.assigned_to.get_full_name() or instance.assigned_to.username,
                    "website_id": instance.website_id
                },
                website=instance.website
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send ticket assigned notification: {e}")
        
        _safe_send_mail(
            f"Ticket Assigned: {instance.title}",
            f"You have been assigned to the ticket '{instance.title}'.",
            getattr(instance.assigned_to, "email", None),
        )

    # Escalation log
    if getattr(instance, "is_escalated", False):
        TicketLog.objects.create(
            ticket=instance,
            action="Ticket escalated to high priority",
            performed_by=instance.created_by,
        )
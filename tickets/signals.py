from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail  # Optional for email notifications
from .models import Ticket, TicketLog
from django.conf import settings

# Signal to log action after ticket creation
@receiver(post_save, sender=Ticket)
def ticket_created(sender, instance, created, **kwargs):
    if created:
        # Log ticket creation
        TicketLog.objects.create(
            ticket=instance,
            action="Ticket created",
            performed_by=instance.created_by
        )
        
        # Optional: Send email notification to support/admin (if needed)
        send_mail(
            f"New Ticket Created: {instance.title}",
            f"A new ticket titled '{instance.title}' has been created.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.website.admin_email],  # Assuming the website has an admin email
        )

# Signal to log action after ticket update (status change, etc.)
@receiver(post_save, sender=Ticket)
def ticket_updated(sender, instance, **kwargs):
    if instance.pk:
        # If the ticket was updated, create a log entry
        TicketLog.objects.create(
            ticket=instance,
            action=f"Ticket updated: Status changed to {instance.status}",
            performed_by=instance.created_by
        )

# Signal to log action after ticket escalation
@receiver(post_save, sender=Ticket)
def ticket_escalated(sender, instance, **kwargs):
    if instance.is_escalated:
        TicketLog.objects.create(
            ticket=instance,
            action="Ticket escalated to high priority",
            performed_by=instance.created_by
        )

# Signal to log action after ticket assignment
@receiver(post_save, sender=Ticket)
def ticket_assigned(sender, instance, **kwargs):
    if instance.assigned_to:
        TicketLog.objects.create(
            ticket=instance,
            action=f"Ticket assigned to {instance.assigned_to.username}",
            performed_by=instance.created_by
        )
        
        # Optional: Send an email to the assignee notifying them
        send_mail(
            f"Ticket Assigned: {instance.title}",
            f"You have been assigned to the ticket '{instance.title}'.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.assigned_to.email],
        )
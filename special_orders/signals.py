from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SpecialOrder, Milestone, ProgressLog
from django.core.mail import send_mail


@receiver(post_save, sender=SpecialOrder)
def notify_client_on_order_status_change(sender, instance, created, **kwargs):
    """
    Notify the client when the status of their special order changes.
    """
    if not created:  # Only act on updates
        status = instance.status
        client_email = instance.client.email

        # Send notification email to the client
        send_mail(
            subject=f"Order #{instance.id} Status Update",
            message=f"Your order status has been updated to '{status}'.",
            from_email='no-reply@yourdomain.com',
            recipient_list=[client_email],
        )


@receiver(post_save, sender=Milestone)
def notify_writer_on_milestone_creation(sender, instance, created, **kwargs):
    """
    Notify the writer when a new milestone is created for a special order.
    """
    if created:
        writer_email = instance.special_order.writer.email

        # Send notification email to the writer
        send_mail(
            subject=f"New Milestone for Order #{instance.special_order.id}",
            message=f"A new milestone '{instance.name}' has been created for your order.",
            from_email='no-reply@yourdomain.com',
            recipient_list=[writer_email],
        )


@receiver(post_save, sender=ProgressLog)
def update_milestone_on_progress_log(sender, instance, created, **kwargs):
    """
    Automatically mark milestones as completed when progress logs are added.
    """
    if created and instance.milestone:
        # Example logic: Mark milestone as completed if all progress is logged
        milestone = instance.milestone
        if not milestone.is_completed:
            milestone.is_completed = True
            milestone.completed_at = instance.progress_date
            milestone.save()
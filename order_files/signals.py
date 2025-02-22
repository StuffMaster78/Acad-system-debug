from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderFile, FileDeletionRequest, ExternalFileLink
from notifications_system.models import Notification  # Assuming Notifications App exists

@receiver(post_save, sender=OrderFile)
def notify_file_uploaded(sender, instance, created, **kwargs):
    """Notify users when a new file is uploaded."""
    if created:
        message = f"New file uploaded to Order {instance.order.id} by {instance.uploaded_by}."
        Notification.objects.create(
            recipient=instance.order.client,  # Notify client
            message=message,
            order=instance.order
        )

@receiver(post_save, sender=FileDeletionRequest)
def notify_deletion_request(sender, instance, created, **kwargs):
    """Notify Admins when a file deletion request is submitted."""
    if created:
        message = f"Deletion request for {instance.file} by {instance.requested_by}."
        Notification.objects.create(
            recipient=instance.file.order.admin,  # Notify admin
            message=message,
            order=instance.file.order
        )

@receiver(post_save, sender=ExternalFileLink)
def notify_external_link_uploaded(sender, instance, created, **kwargs):
    """Notify Admins when a new external file link is uploaded."""
    if created:
        message = f"New external file link submitted for Order {instance.order.id} by {instance.uploaded_by}."
        Notification.objects.create(
            recipient=instance.order.admin,  # Notify admin
            message=message,
            order=instance.order
        )
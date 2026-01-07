from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderFile, FileDeletionRequest, ExternalFileLink
from notifications_system.models import Notification
from notifications_system.utils.in_app_helpers import send_in_app_notification

@receiver(post_save, sender=OrderFile)
def notify_file_uploaded(sender, instance, created, **kwargs):
    """Notify users when a new file is uploaded.
    
    Notifies:
    1. The uploader (themselves) - "You uploaded a file"
    2. The other party (client if writer uploaded, writer if client uploaded)
    """
    if not created:
        return
    
    order = instance.order
    uploaded_by = instance.uploaded_by
    website = getattr(order, 'website', None)
    
    if not website:
        return
    
    # Get file name for display
    file_name = instance.file.name.split('/')[-1] if instance.file else "a file"
    uploader_role = getattr(uploaded_by, 'role', None) if uploaded_by else None
    
    # 1. Notify the uploader (themselves) - "You uploaded a file"
    if uploaded_by:
        uploader_message = f"You uploaded {file_name} to order #{order.id}"
        
        try:
            send_in_app_notification(
                user=uploaded_by,
                title="File Uploaded",
                message=uploader_message,
                website=website,
                event_key="order.file_uploaded",
                data={"order_id": order.id, "file_id": instance.id, "uploaded_by_you": True}
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to notify uploader about file upload: {e}")
    
    # 2. Notify the other party (client if writer uploaded, writer if client uploaded)
    if uploader_role == 'writer' and order.client and order.client != uploaded_by:
        # Writer uploaded - notify client
        client_message = f"Writer uploaded {file_name} to order #{order.id}"
        
        try:
            send_in_app_notification(
                user=order.client,
                title="New File Uploaded",
                message=client_message,
                website=website,
                event_key="order.file_uploaded",
                data={"order_id": order.id, "file_id": instance.id, "uploaded_by_you": False}
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to notify client about file upload: {e}")
    elif uploader_role == 'client' and order.assigned_writer and order.assigned_writer != uploaded_by:
        # Client uploaded - notify writer
        writer_message = f"Client uploaded {file_name} to order #{order.id}"
        
        try:
            send_in_app_notification(
                user=order.assigned_writer,
                title="New File Uploaded",
                message=writer_message,
                website=website,
                event_key="order.file_uploaded",
                data={"order_id": order.id, "file_id": instance.id, "uploaded_by_you": False}
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to notify writer about file upload: {e}")

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
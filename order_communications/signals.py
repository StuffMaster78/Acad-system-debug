from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import OrderMessage, OrderMessageNotification, FlaggedMessage, DisputeMessage


@receiver(post_save, sender=OrderMessage)
def notify_user_on_new_message(sender, instance, created, **kwargs):
    """
    Notify users when a new message is sent.
    Includes message preview in notification.
    """
    if created:
        recipient = None
        order = instance.thread.order
        message_preview = instance.message[:50] + ("..." if len(instance.message) > 50 else "")

        if instance.sender_role == "client":
            recipient = getattr(order, "writer", None)  # Get writer if available
        else:
            recipient = getattr(order, "client", None)  # Get client if available

        if recipient:
            OrderMessageNotification.objects.create(
                recipient=recipient,
                message=instance,
                notification_text=f"New message: {message_preview}",
                is_read=False
            )


@receiver(post_save, sender=FlaggedMessage)
def notify_admin_on_flagged_message(sender, instance, created, **kwargs):
    """
    Notify admins when a message is flagged for review.
    Includes message preview and expiration time.
    """
    if created:
        admin_users = get_user_model().objects.filter(is_staff=True)
        message_preview = instance.order_message.message[:50] + ("..." if len(instance.order_message.message) > 50 else "")
        notifications = [
            OrderMessageNotification(
                recipient=admin,
                message=instance.order_message,
                notification_text=f"🚨 Flagged Message: {message_preview}",
                is_read=False
            )
            for admin in admin_users
        ]
        
        # Bulk insert notifications for performance optimization
        OrderMessageNotification.objects.bulk_create(notifications)





@receiver(post_save, sender=DisputeMessage)
def notify_admin_on_new_dispute(sender, instance, created, **kwargs):
    """
    Notify admins when a new dispute message is created.
    """
    if created:
        admin_users = get_user_model().objects.filter(is_staff=True)
        notifications = [
            OrderMessageNotification(
                recipient=admin,
                message=instance.order_message,
                notification_text=f"New dispute message from {instance.sender.username}: {instance.message}",
                is_read=False
            )
            for admin in admin_users
        ]
        
        # Bulk insert notifications for performance optimization
        OrderMessageNotification.objects.bulk_create(notifications)


@receiver(post_save, sender=DisputeMessage)
def notify_admin_on_resolved_dispute(sender, instance, created, **kwargs):
    """
    Notify admins when a dispute message is resolved.
    """
    if not created and instance.status == "resolved":
        admin_users = get_user_model().objects.filter(is_staff=True)
        notifications = [
            OrderMessageNotification(
                recipient=admin,
                message=instance.order_message,
                notification_text=f"Dispute resolved for Order {instance.order_message.thread.order.id} - {instance.resolution_comment}",
                is_read=False
            )
            for admin in admin_users
        ]
        
        # Bulk insert notifications for performance optimization
        OrderMessageNotification.objects.bulk_create(notifications)

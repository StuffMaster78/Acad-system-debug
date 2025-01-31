from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import AdminLog
from notifications_system.models import send_notification  # Import from Notifications App

User = get_user_model()

@receiver(post_save, sender=User)
def notify_superadmins_on_new_admin(sender, instance, created, **kwargs):
    """Notifies Superadmins when a new Admin is added."""
    if created and instance.role == "admin":
        send_notification(
            recipient=User.objects.filter(role="superadmin"),
            title="New Admin Added",
            message=f"{instance.username} has been assigned as an Admin.",
            category="user"
        )


@receiver(post_save, sender=User)
def log_admin_suspensions(sender, instance, **kwargs):
    """Logs when an Admin suspends a user."""
    if instance.is_suspended:
        AdminLog.objects.create(
            admin=instance,
            action=f"Suspended {instance.username}."
        )


from orders.models import Dispute

@receiver(post_save, sender=Dispute)
def notify_admins_on_new_dispute(sender, instance, created, **kwargs):
    """Notifies Admins when a new dispute is created."""
    if created:
        send_notification(
            recipient=User.objects.filter(role="admin"),
            title="New Dispute Opened",
            message=f"A dispute for Order #{instance.order.id} was opened by {instance.user.username}.",
            category="dispute"
        )

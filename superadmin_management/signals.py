from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import SuperadminLog
from django.contrib.auth import get_user_model
from .utils import SuperadminNotifier
from orders.models import Dispute

User = get_user_model()

@receiver(post_save, sender=User)
def notify_superadmins_on_new_user(sender, instance, created, **kwargs):
    """Sends a notification when a new user is created."""
    if created:
        superadmins = User.objects.filter(role="superadmin")
        for superadmin in superadmins:
            send_mail(
                subject="New User Created",
                message=f"A new user, {instance.username} ({instance.role}), has been created.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[superadmin.email],
                fail_silently=True,
            )
            # Log the action
            SuperadminLog.objects.create(
                superadmin=superadmin,
                action=f"New user created: {instance.username} ({instance.role})"
            )

@receiver(post_save, sender=User)
def notify_user_on_suspension(sender, instance, **kwargs):
    """Sends a notification when a user is suspended or reactivated."""
    if instance.is_suspended:
        send_mail(
            subject="Account Suspended",
            message="Your account has been suspended. Please contact support for more details.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,
        )
    elif not instance.is_suspended and instance.suspension_reason is None:
        send_mail(
            subject="Account Reactivated",
            message="Your account has been reactivated. You can now log in.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,
        )



@receiver(post_save, sender=User)
def notify_superadmins_on_new_user(sender, instance, created, **kwargs):
    """Sends a notification when a new user is created."""
    if created:
        SuperadminNotifier.notify_superadmins(
            title="New User Registered",
            message=f"A new user {instance.username} ({instance.role}) has registered.",
            category="user"
        )


@receiver(post_save, sender=User)
def notify_superadmins_on_user_suspension(sender, instance, **kwargs):
    """Notifies Superadmins when a user is suspended."""
    if instance.is_suspended:
        SuperadminNotifier.notify_superadmins(
            title="User Suspended",
            message=f"{instance.username} ({instance.role}) has been suspended.",
            category="security"
        )


from client_management.models import BlacklistedEmail

@receiver(post_save, sender=BlacklistedEmail)
def notify_superadmins_on_blacklisted_email(sender, instance, **kwargs):
    """Notifies Superadmins when an email is blacklisted."""
    SuperadminNotifier.notify_superadmins(
        title="Blacklisted Email",
        message=f"The email {instance.email} has been blacklisted.",
        category="security"
    )


from orders.models import PaymentTransaction

@receiver(post_save, sender=PaymentTransaction)
def notify_superadmins_on_large_payment(sender, instance, created, **kwargs):
    """Notifies Superadmins when a high-value payment is made."""
    if created and instance.amount > 1000:  # Adjust threshold as needed
        SuperadminNotifier.notify_superadmins(
            title="High-Value Payment",
            message=f"A payment of ${instance.amount} has been processed by {instance.user.username}.",
            category="financial"
        )



@receiver(post_save, sender=Dispute)
def notify_superadmins_on_dispute(sender, instance, created, **kwargs):
    """Notifies Superadmins when a new dispute is created."""
    if created:
        SuperadminNotifier.notify_superadmins(
            title="New Order Dispute",
            message=f"A dispute has been opened for Order #{instance.order.id} by {instance.user.username}.",
            category="dispute"
        )

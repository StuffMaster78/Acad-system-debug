from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

from .models import SuperadminLog
from .utils import SuperadminNotifier
from orders.models.order_disputes import Dispute
from client_management.models import BlacklistedEmail

# from orders.models import FailedPayment
from admin_management.models import AdminPromotionRequest

User = settings.AUTH_USER_MODEL


### 🔹 1️⃣ Notify Superadmins When a New User is Created
@receiver(post_save, sender=User)
def notify_superadmins_on_new_user(sender, instance, created, **kwargs):
    """Sends a notification when a new user is created."""
    # Skip if signals are disabled (e.g., during testing)
    if getattr(settings, "DISABLE_NOTIFICATION_SIGNALS", False):
        return
    
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
                action_type="user_manage",
                action_details=f"New user created: {instance.username} ({instance.role})"
            )

        # Send in-app notification
        # Get website from the new user instance
        try:
            website = getattr(instance, 'website', None)
            if not website:
                from websites.models.websites import Website
                website = Website.objects.filter(is_active=True).first()
            
            if website:
                SuperadminNotifier.notify_superadmins(
                    title="New User Registered",
                    message=f"A new user {instance.username} ({instance.role}) has registered.",
                    category="user",
                    website=website
                )
        except (ConnectionRefusedError, OSError) as e:
            # Non-critical: notification service unavailable
            logger.debug(f"Could not send superadmin notification (service unavailable): {e}")
        except Exception as e:
            logger.warning(f"Failed to send superadmin notification: {e}", exc_info=True)


### 🔹 2️⃣ Notify Users When Suspended or Reactivated
@receiver(post_save, sender=User)
def notify_user_on_suspension(sender, instance, update_fields=None, **kwargs):
    """Sends a notification when a user is suspended or reactivated."""
    # Skip if signals are disabled (e.g., during testing)
    if getattr(settings, "DISABLE_NOTIFICATION_SIGNALS", False):
        return
    
    if update_fields and 'is_suspended' not in update_fields:
        return  # Skip if the suspension status didn't change

    if instance.is_suspended:
        send_mail(
            subject="Account Suspended",
            message="Your account has been suspended. Please contact support for more details.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,
        )
    else:
        send_mail(
            subject="Account Reactivated",
            message="Your account has been reactivated. You can now log in.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=True,
        )

    # Notify Superadmins
    try:
        website = getattr(instance, 'website', None)
        if not website:
            from websites.models.websites import Website
            website = Website.objects.filter(is_active=True).first()
        
        if website:
            SuperadminNotifier.notify_superadmins(
                title="User Suspended" if instance.is_suspended else "User Reactivated",
                message=f"{instance.username} ({instance.role}) has been {'suspended' if instance.is_suspended else 'reactivated'}.",
                category="security",
                website=website
            )
    except (ConnectionRefusedError, OSError) as e:
        logger.debug(f"Could not send superadmin notification (service unavailable): {e}")
    except Exception as e:
        logger.warning(f"Failed to send superadmin notification: {e}", exc_info=True)


### 🔹 3️⃣ Notify Superadmins When an Email is Blacklisted
@receiver(post_save, sender=BlacklistedEmail)
def notify_superadmins_on_blacklisted_email(sender, instance, **kwargs):
    """Notifies Superadmins when an email is blacklisted."""
    from websites.models.websites import Website
    website = Website.objects.filter(is_active=True).first()
    
    if website:
        SuperadminNotifier.notify_superadmins(
            title="Blacklisted Email",
            message=f"The email {instance.email} has been blacklisted.",
            category="security",
            website=website
        )


# ### 🔹 4️⃣ Notify Superadmins for High-Value Payments
# @receiver(post_save, sender=PaymentTransaction)
# def notify_superadmins_on_large_payment(sender, instance, created, **kwargs):
#     """Notifies Superadmins when a high-value payment is made."""
#     if created and instance.amount > 1000:  # Adjust threshold as needed
#         SuperadminNotifier.notify_superadmins(
#             title="High-Value Payment",
#             message=f"A payment of ${instance.amount} has been processed by {instance.user.username}.",
#             category="financial"
#         )


### 🔹 5️⃣ Notify Superadmins When a Dispute is Created
@receiver(post_save, sender=Dispute)
def notify_superadmins_on_dispute(sender, instance, created, **kwargs):
    """Notifies Superadmins when a new dispute is created."""
    if created:
        # Get website from order or user
        website = getattr(instance.order, 'website', None) or getattr(instance.user, 'website', None)
        if not website:
            from websites.models.websites import Website
            website = Website.objects.filter(is_active=True).first()
        
        if website:
            SuperadminNotifier.notify_superadmins(
                title="New Order Dispute",
                message=f"A dispute has been opened for Order #{instance.order.id} by {instance.user.username}.",
                category="dispute",
                website=website
            )



# ### 🔹 Notify Superadmins on Failed Payments
# @receiver(post_save, sender=FailedPayment)
# def notify_superadmins_on_failed_payment(sender, instance, created, **kwargs):
#     """Notifies Superadmins when a payment fails."""
#     if created:
#         SuperadminNotifier.notify_superadmins(
#             title="Failed Payment",
#             message=f"A payment of ${instance.amount} from {instance.user.username} has failed.",
#             category="financial"
#         )

### 🔹 Notify Superadmins on Admin Promotions
@receiver(post_save, sender=AdminPromotionRequest)
def notify_superadmins_on_admin_promotion_request(sender, instance, created, **kwargs):
    """Notifies Superadmins when an admin promotion request is submitted."""
    if created:
        # Get website from user
        website = getattr(instance.user, 'website', None)
        if not website:
            from websites.models.websites import Website
            website = Website.objects.filter(is_active=True).first()
        
        if website:
            SuperadminNotifier.notify_superadmins(
                title="Admin Promotion Request",
                message=f"{instance.user.username} has requested a promotion to {instance.requested_role}.",
                category="admin",
                website=website
            )

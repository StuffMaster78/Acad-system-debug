from django.db.models.signals import post_save
from django.dispatch import receiver
from wallet.models import WalletTransaction
from .models import Notification
from core.utils import send_notification
from users.models import User
from notifications_system.models.notification_preferences import NotificationPreference
# from notifications_system.models.digest_notifications import  NotificationDigest
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from notifications_system.services.preferences import NotificationPreferenceResolver
from notifications_system.services.preferences_cache import update_preferences_cache
from django.core.cache import cache
import logging
from django.template.loader import render_to_string
from django.core.mail import send_mail
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def notify_via_ws(notification):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{notification.user.id}",
        {
            "type": "send_notification",
            "message": notification.message,
            "context": notification.context,
        }
    )


def send_email(to_email, subject, message, html_message=None):
    """
    Wrapper for Django's send_mail function to send emails.
    """
    send_mail(
        subject,
        message,
        'no-reply@example.com',  # Replace with your default from email
        [to_email],
        html_message=html_message,
        fail_silently=False,
    )

def render_template(templates, context):
    """
    Renders a template with the given context.
    """
    if isinstance(templates, (list, tuple)):
        for template_name in templates:
            try:
                return render_to_string(template_name, context)
            except Exception:
                continue
        raise Exception("None of the templates could be rendered.")
    return render_to_string(templates, context)

@receiver(post_save, sender=User)
def ensure_user_notification_pref(sender, instance, created, **kwargs):
    if created:
        NotificationPreferenceResolver.assign_default_preferences(instance, instance.website)
    update_preferences_cache(instance)


@receiver(post_save, sender=WalletTransaction)
def notify_wallet_transaction(sender, instance, created, **kwargs):
    """
    Create and send notifications when a wallet transaction occurs.
    """
    if created:
        Notification.objects.create(
            user=instance.wallet.user,
            type="in_app",
            title="Wallet Transaction",
            message=f"A transaction of ${instance.amount:.2f} was made on your wallet.",
            website=instance.wallet.website,
        )
        send_notification(
            instance.wallet.user,
            f"A transaction of ${instance.amount:.2f} was made on your wallet.",
            notification_type="email"
        )


@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def auto_create_notif_preferences(sender, instance, created, **kwargs):
    if created:
        NotificationPreferenceResolver.assign_default_preferences(instance, instance.website)
        cache.set(f"notif_prefs:{instance.id}", instance.notification_preferences, timeout=3600)

@receiver(post_save, sender=Notification)
def update_notification_cache(sender, instance, **kwargs):
    """
    Update the notification cache when a notification is created or updated.
    """
    cache_key = f"notification:{instance.user_id}"
    cache.set(cache_key, instance, timeout=3600)
    logger.info(f"Notification cache updated for user {instance.user_id}.")

@receiver(post_save, sender=Notification)
def clear_notification_cache(sender, instance, **kwargs):
    """
    Clear the notification cache when a notification is deleted.
    """
    cache_key = f"notification:{instance.user_id}"
    cache.delete(cache_key)
    logger.info(f"Notification cache cleared for user {instance.user_id}.")
from django.db.models.signals import post_save
from django.dispatch import receiver
from wallet.models import WalletTransaction
from .models.notifications import Notification
from notifications_system.services.dispatch import NotificationDispatcher
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
import logging
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache

from notifications_system.models.notification_preferences import (
    NotificationPreference,
)
from notifications_system.models.notification_profile import (
    NotificationGroupProfile,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from notifications_system.models.user_notification_meta import UserNotificationMeta

from django.dispatch import receiver
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.utils.unread_counter import incr, decr, invalidate

User = get_user_model()


User = get_user_model()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def _ensure_notif_meta(sender, instance, created, **kwargs):
    if created:
        UserNotificationMeta.objects.get_or_create(user=instance)

@receiver(post_save, sender=Notification)
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

@receiver(post_save, sender=Notification)
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
        NotificationDispatcher.dispatch(
            instance.wallet.user,
            f"A transaction of ${instance.amount:.2f} was made on your wallet.",
            notification_type="email",
            context={"transaction": instance}
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



# -----------------
# Cache helpers
# -----------------

def _cache_key(user_id: int, website_id: Optional[int]) -> str:
    """Build the effective-preferences cache key."""
    wid = website_id if website_id is not None else "none"
    return f"notif_prefs:{user_id}:{wid}"


def _invalidate_user_cache(user, website) -> None:
    """Delete the effective-preferences cache for one user/site."""
    if not user:
        return
    wid = getattr(website, "id", None)
    cache.delete(_cache_key(user.id, wid))


# --------------------------------------------
# 1) User-level preference changes → invalidate
# --------------------------------------------

@receiver(post_save, sender=NotificationPreference, dispatch_uid="np_ps")
@receiver(post_delete, sender=NotificationPreference, dispatch_uid="np_pd")
def _on_user_pref_changed(sender, instance, **kwargs):
    """Invalidate cache when a user's preference row changes."""
    user = getattr(instance, "user", None)
    website = getattr(instance, "website", None)
    _invalidate_user_cache(user, website)


# -------------------------------------------------------
# 2) Group profile changes → invalidate all users in group
# -------------------------------------------------------

@receiver(
    post_save, sender=NotificationGroupProfile, dispatch_uid="ngp_ps"
)
@receiver(
    post_delete, sender=NotificationGroupProfile, dispatch_uid="ngp_pd"
)
def _on_group_profile_changed(sender, instance, **kwargs):
    """Invalidate caches for all users impacted by a group profile."""
    group = getattr(instance, "group", None)
    website = getattr(instance, "website", None)
    if not group:
        return

    user_ids = (
        User.objects.filter(groups=group)
        .values_list("id", flat=True)
        .iterator()
    )
    wid = getattr(website, "id", None)
    keys = [_cache_key(uid, wid) for uid in user_ids]
    if keys:
        cache.delete_many(keys)


# ----------------------------------------------------
# 3) User.group membership changes → invalidate that user
# ----------------------------------------------------

try:
    # m2m_changed works on the through model of the M2M relation.
    through = User.groups.through  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - custom user model might differ
    through = None


if through is not None:
    @receiver(m2m_changed, sender=through, dispatch_uid="user_groups_m2m")
    def _on_user_groups_changed(sender, instance, action, **kwargs):
        """Invalidate when a user's group membership changes.

        Args:
            instance: The User instance.
            action: m2m action (e.g., "post_add", "post_remove", "post_clear").
        """
        if action in {"post_add", "post_remove", "post_clear"}:
            website = getattr(instance, "website", None)
            _invalidate_user_cache(instance, website)



def _website_id_of(status):
    n = getattr(status, "notification", None)
    return getattr(getattr(n, "website", None), "id", None)

@receiver(post_save, sender=NotificationsUserStatus)
def _on_status_save(sender, instance: NotificationsUserStatus, created, **kwargs):
    wid = _website_id_of(instance)
    if created and not instance.is_read:
        incr(instance.user_id, wid)
    else:
        # if it flipped to read
        if "update_fields" in kwargs and kwargs["update_fields"]:
            if "is_read" in kwargs["update_fields"] and instance.is_read:
                decr(instance.user_id, wid)

@receiver(post_delete, sender=NotificationsUserStatus)
def _on_status_delete(sender, instance: NotificationsUserStatus, **kwargs):
    # conservative approach: if unread at delete, decrement; else no-op
    if not instance.is_read:
        decr(instance.user_id, _website_id_of(instance))
# notifications_system/signals.py
from __future__ import annotations
from django.conf import settings
import logging
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from wallet.models import WalletTransaction

from notifications_system.models.notifications import Notification
from notifications_system.models.notification_preferences import NotificationPreference
from notifications_system.models.notification_profile import NotificationGroupProfile
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.models.user_notification_meta import UserNotificationMeta

from notifications_system.services.dispatch import send
from notifications_system.services.preferences import NotificationPreferenceResolver
from notifications_system.services.preferences_cache import update_preferences_cache

User = get_user_model()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Helpers (plain functions — NOT signal receivers)
# ---------------------------------------------------------------------

def send_email_helper(to_email: str, subject: str, message: str, html_message=None) -> None:
    """Thin wrapper over Django send_mail for consistency."""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        html_message=html_message,
        fail_silently=False,
    )

def render_template_helper(templates, context) -> str:
    """Render the first template that works from a list or a single template."""
    if isinstance(templates, (list, tuple)):
        for template_name in templates:
            try:
                return render_to_string(template_name, context)
            except Exception:
                continue
        raise RuntimeError("None of the templates could be rendered.")
    return render_to_string(templates, context)

def _cache_key(user_id: int, website_id: Optional[int]) -> str:
    wid = website_id if website_id is not None else "none"
    return f"notif_prefs:{user_id}:{wid}"

def _invalidate_user_cache(user, website) -> None:
    if not user:
        return
    wid = getattr(website, "id", None)
    cache.delete(_cache_key(user.id, wid))

def _website_id_of(status: NotificationsUserStatus) -> Optional[int]:
    n = getattr(status, "notification", None)
    return getattr(getattr(n, "website", None), "id", None)

# ---------------------------------------------------------------------
# User lifecycle
# ---------------------------------------------------------------------

@receiver(post_save, sender=User, dispatch_uid="user_meta_post_save_v1")
def _ensure_notif_meta(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return
    if created:
        UserNotificationMeta.objects.get_or_create(user=instance)

@receiver(post_save, sender=User, dispatch_uid="user_pref_assign_defaults_v1")
def ensure_user_notification_pref(sender, instance, created, **kwargs):
    if getattr(settings, "DISABLE_NOTIFICATION_SIGNALS", False):
        return
    if kwargs.get("raw"):
        return
    # Only create preferences on user creation, not on every save (like login updates)
    if created and instance.website:  # Only create preferences for users with websites
        # Check if preference already exists to avoid duplicates
        from notifications_system.models.notification_preferences import NotificationPreference
        if not NotificationPreference.objects.filter(user=instance).exists():
            NotificationPreferenceResolver.assign_default_preferences(
                instance, instance.website
            )
    if instance.website:  # Only update cache for users with websites
        update_preferences_cache(instance)

@receiver(post_save, sender=User, dispatch_uid="user_pref_create_row_v1")
def create_notification_preferences(sender, instance, created, **kwargs):
    if getattr(settings, "DISABLE_NOTIFICATION_SIGNALS", False):
        return
    if kwargs.get("raw"):
        return
    # Only create preferences on user creation, not on every save (like login updates)
    if created and instance.website:  # Only create preferences for users with websites
        # Check if preference already exists to avoid duplicates
        from notifications_system.models.notification_preferences import NotificationPreference
        NotificationPreference.objects.get_or_create(
            user=instance, 
            website=instance.website,
            defaults={}  # Will be populated by assign_default_preferences
        )

@receiver(post_save, sender=User, dispatch_uid="user_pref_cache_seed_v1")
def auto_create_notif_preferences(sender, instance, created, **kwargs):
    if getattr(settings, "DISABLE_NOTIFICATION_SIGNALS", False):
        return
    if kwargs.get("raw"):
        return
    # Only create preferences on user creation, not on every save (like login updates)
    if created and instance.website:  # Only create preferences for users with websites
        # Check if preference already exists to avoid duplicates
        from notifications_system.models.notification_preferences import NotificationPreference
        if not NotificationPreference.objects.filter(user=instance).exists():
            NotificationPreferenceResolver.assign_default_preferences(
                instance, instance.website
            )
            cache.set(
                f"notif_prefs:{instance.id}",
                instance.notification_preferences,
                timeout=3600,
            )

# ---------------------------------------------------------------------
# Wallet transactions
# ---------------------------------------------------------------------

@receiver(post_save, sender=WalletTransaction, dispatch_uid="wallet_tx_notify_v1")
def notify_wallet_transaction(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return
    if created:
        Notification.objects.create(
            user=instance.wallet.user,
            type="in_app",
            title="Wallet Transaction",
            message=f"A transaction of ${instance.amount:.2f} was made on your wallet.",
            website=instance.wallet.website,
        )
        send(
            user=instance.wallet.user,
            message=f"A transaction of ${instance.amount:.2f} was made on your wallet.",
            notification_type="email",
            context={"transaction": instance},
        )

# ---------------------------------------------------------------------
# Notification cache
# ---------------------------------------------------------------------
@receiver([post_save, post_delete], sender=NotificationPreference)
def _refresh_pref_cache(sender, instance, **kwargs):
    """Refresh notification preferences cache on changes."""
    NotificationPreferenceResolver.update_preferences_cache(instance.user)

@receiver(post_save, sender=Notification, dispatch_uid="notif_cache_update_v1")
def update_notification_cache(sender, instance, **kwargs):
    """Update per-user notification cache on create/update."""
    cache_key = f"notification:{instance.user_id}"
    cache.set(cache_key, instance, timeout=3600)
    logger.info("Notification cache updated for user %s.", instance.user_id)

@receiver(post_delete, sender=Notification, dispatch_uid="notif_cache_clear_v1")
def clear_notification_cache(sender, instance, **kwargs):
    """Clear per-user notification cache on delete."""
    cache_key = f"notification:{instance.user_id}"
    cache.delete(cache_key)
    logger.info("Notification cache cleared for user %s.", instance.user_id)

# ---------------------------------------------------------------------
# Preferences invalidation
# ---------------------------------------------------------------------

@receiver(post_save, sender=NotificationPreference, dispatch_uid="np_ps")
@receiver(post_delete, sender=NotificationPreference, dispatch_uid="np_pd")
def _on_user_pref_changed(sender, instance, **kwargs):
    user = getattr(instance, "user", None)
    website = getattr(instance, "website", None)
    _invalidate_user_cache(user, website)

@receiver(post_save, sender=NotificationGroupProfile, dispatch_uid="ngp_ps")
@receiver(post_delete, sender=NotificationGroupProfile, dispatch_uid="ngp_pd")
def _on_group_profile_changed(sender, instance, **kwargs):
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

# m2m: user.groups changes
try:
    through = User.groups.through  # type: ignore[attr-defined]
except Exception:
    through = None

if through is not None:
    @receiver(m2m_changed, sender=through, dispatch_uid="user_groups_m2m_v1")
    def _on_user_groups_changed(sender, instance, action, reverse, model, pk_set, using, **kwargs):
        if action in {"post_add", "post_remove", "post_clear"}:
            website = getattr(instance, "website", None)
            _invalidate_user_cache(instance, website)

# ---------------------------------------------------------------------
# NotificationsUserStatus counters
# ---------------------------------------------------------------------

@receiver(post_save, sender=NotificationsUserStatus, dispatch_uid="nus_post_save_v1")
def _on_status_save(sender, instance: NotificationsUserStatus, created, **kwargs):
    wid = _website_id_of(instance)
    if created and not instance.is_read:
        from notifications_system.utils.unread_counter import incr
        incr(instance.user_id, wid)
    else:
        # decrement only when flipped to read on update
        update_fields = kwargs.get("update_fields") or set()
        if "is_read" in update_fields and instance.is_read:
            from notifications_system.utils.unread_counter import decr
            decr(instance.user_id, wid)

@receiver(post_delete, sender=NotificationsUserStatus, dispatch_uid="nus_post_delete_v1")
def _on_status_delete(sender, instance: NotificationsUserStatus, **kwargs):
    if not instance.is_read:
        from notifications_system.utils.unread_counter import decr
        decr(instance.user_id, _website_id_of(instance))

"""
Notification system signals.
Invalidates template cache when templates are saved.
Invalidates preference cache when preferences are saved.
"""
from __future__ import annotations

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver([post_save, post_delete], sender='notifications_system.NotificationTemplate')
def invalidate_template_cache(sender, instance, **kwargs):
    """Invalidate template cache when a template is saved or deleted."""
    try:
        from notifications_system.services.template_service import TemplateService
        TemplateService.invalidate_cache(
            event_key=instance.event.event_key,
            channel=instance.channel,
            website=instance.website,
        )
    except Exception:
        pass


@receiver(post_save, sender='notifications_system.NotificationPreference')
def invalidate_preference_cache(sender, instance, **kwargs):
    """Invalidate preference cache when preferences are saved."""
    try:
        from notifications_system.services.preference_service import PreferenceService
        PreferenceService._invalidate_cache(instance.user, instance.website)
    except Exception:
        pass


@receiver(post_save, sender='notifications_system.NotificationEventPreference')
def invalidate_event_preference_cache(sender, instance, **kwargs):
    """Invalidate preference cache when event preferences are saved."""
    try:
        from notifications_system.services.preference_service import PreferenceService
        PreferenceService._invalidate_cache(instance.user, instance.website)
    except Exception:
        pass
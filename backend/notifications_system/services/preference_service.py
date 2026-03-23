# notifications_system/services/preference_service.py
"""
Preference resolution for the notification system.

Resolution order (highest to lowest priority):
    1. NotificationEventPreference  — per-user, per-event override
    2. NotificationPreference       — per-user master settings
    3. RoleNotificationPreference   — per-role defaults
    4. NotificationEventConfig      — event config defaults
    5. In-app fallback              — always works
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from django.utils import timezone

from notifications_system.enums import NotificationChannel

logger = logging.getLogger(__name__)

PREF_CACHE_TTL = 3600  # 1 hour


class PreferenceService:
    """
    Single service for all preference checks.
    Called by NotificationDispatcher before any delivery.
    """

    # -------------------------
    # Core delivery gate
    # -------------------------

    @staticmethod
    def should_notify(user, website, event_key: str, channel: str) -> bool:
        """
        Returns True if the user should receive this notification
        on this channel.

        Checks in order:
            1. Mandatory events always fire
            2. Per-event preference
            3. Master preference channel toggle
            4. Role default
            5. Event config default
        """
        from notifications_system.models.event_config import NotificationEventConfig
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
            NotificationEventPreference,
            RoleNotificationPreference,
        )

        # 1. Mandatory events always fire
        try:
            config = NotificationEventConfig.objects.get(
                event__event_key=event_key,
                is_active=True,
            )
            if config.is_mandatory:
                return True
        except NotificationEventConfig.DoesNotExist:
            config = None

        # 2. Per-event preference
        try:
            event_pref = NotificationEventPreference.objects.get(
                user=user,
                website=website,
                event__event_key=event_key,
            )
            if not event_pref.is_enabled:
                return False
            if channel == NotificationChannel.EMAIL:
                return event_pref.email_enabled
            if channel == NotificationChannel.IN_APP:
                return event_pref.in_app_enabled
        except NotificationEventPreference.DoesNotExist:
            pass

        # 3. Master preference channel toggle
        try:
            pref = NotificationPreference.objects.get(
                user=user,
                website=website,
            )
            if channel == NotificationChannel.EMAIL:
                return pref.email_enabled
            if channel == NotificationChannel.IN_APP:
                return pref.in_app_enabled
        except NotificationPreference.DoesNotExist:
            pass

        # 4. Role default
        role = getattr(user, 'role', None)
        if role:
            try:
                role_pref = RoleNotificationPreference.objects.get(
                    role=role,
                    website=website,
                )
                if channel == NotificationChannel.EMAIL:
                    return role_pref.email_enabled
                if channel == NotificationChannel.IN_APP:
                    return role_pref.in_app_enabled
            except RoleNotificationPreference.DoesNotExist:
                pass

        # 5. Event config default
        if config:
            return config.is_enabled_for_channel(channel)

        return True

    @staticmethod
    def is_muted(user, website) -> bool:
        """
        Returns True if all notifications are currently suppressed for user.
        Checks mute_all flag and mute_until datetime.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
        )
        try:
            pref = NotificationPreference.objects.get(
                user=user,
                website=website,
            )
            return pref.is_muted()
        except NotificationPreference.DoesNotExist:
            return False

    @staticmethod
    def is_in_dnd(user, website) -> bool:
        """
        Returns True if current time falls within the user's DND hours.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
        )
        try:
            pref = NotificationPreference.objects.get(
                user=user,
                website=website,
            )
            return pref.is_in_dnd()
        except NotificationPreference.DoesNotExist:
            return False

    # -------------------------
    # Channel resolution
    # -------------------------

    @staticmethod
    def get_active_channels(user, website) -> List[str]:
        """
        Returns list of currently enabled channels for a user.
        Used by NotificationService to resolve default channels.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
        )
        try:
            pref = NotificationPreference.objects.get(
                user=user,
                website=website,
            )
            return pref.get_active_channels()
        except NotificationPreference.DoesNotExist:
            pass

        # Fall back to role defaults
        return PreferenceService._get_role_channels(user, website)

    @staticmethod
    def _get_role_channels(user, website) -> List[str]:
        """Returns default channels for the user's role."""
        from notifications_system.models.notification_preferences import (
            RoleNotificationPreference,
        )
        role = getattr(user, 'role', None)
        if not role:
            return [NotificationChannel.IN_APP]

        try:
            role_pref = RoleNotificationPreference.objects.get(
                role=role,
                website=website,
            )
            channels = []
            if role_pref.email_enabled:
                channels.append(NotificationChannel.EMAIL)
            if role_pref.in_app_enabled:
                channels.append(NotificationChannel.IN_APP)
            return channels or [NotificationChannel.IN_APP]
        except RoleNotificationPreference.DoesNotExist:
            return [NotificationChannel.IN_APP]

    # -------------------------
    # Preference management
    # -------------------------

    @staticmethod
    def get_or_create_preference(user, website):
        """
        Returns the user's NotificationPreference, creating it if needed.
        Applies default profile if one exists for the website.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
        )

        pref, created = NotificationPreference.objects.get_or_create(
            user=user,
            website=website,
        )

        if created:
            PreferenceService._apply_default_profile(pref, website)
            PreferenceService._seed_event_preferences(user, website)
            logger.info(
                "Created default preferences for user=%s website=%s.",
                user.id,
                website.id,
            )

        return pref

    @staticmethod
    def _apply_default_profile(pref, website) -> None:
        """Apply the website's default profile to a new preference row."""
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )
        profile = NotificationPreferenceProfile.objects.filter(
            website=website,
            is_default=True,
            is_active=True,
        ).first()

        if not profile:
            # Try global default profile
            profile = NotificationPreferenceProfile.objects.filter(
                website__isnull=True,
                is_default=True,
                is_active=True,
            ).first()

        if profile:
            pref.profile = profile
            pref.email_enabled = profile.email_enabled
            pref.in_app_enabled = profile.in_app_enabled
            pref.dnd_enabled = profile.dnd_enabled
            pref.dnd_start_hour = profile.dnd_start_hour
            pref.dnd_end_hour = profile.dnd_end_hour
            pref.digest_enabled = profile.digest_enabled
            pref.digest_frequency = profile.digest_frequency
            pref.save(update_fields=[
                'profile', 'email_enabled', 'in_app_enabled',
                'dnd_enabled', 'dnd_start_hour', 'dnd_end_hour',
                'digest_enabled', 'digest_frequency',
            ])

    @staticmethod
    def _seed_event_preferences(user, website) -> None:
        """
        Create per-event preference rows for all active events.
        Allows users to later toggle individual events on/off.
        """
        from notifications_system.models.notification_event import NotificationEvent
        from notifications_system.models.notification_preferences import (
            NotificationEventPreference,
        )

        events = NotificationEvent.objects.filter(is_active=True)
        NotificationEventPreference.objects.bulk_create(
            [
                NotificationEventPreference(
                    user=user,
                    website=website,
                    event=event,
                )
                for event in events
            ],
            ignore_conflicts=True,
        )

    @staticmethod
    def update_preference(user, website, **fields) -> None:
        """
        Update specific fields on a user's NotificationPreference.
        Invalidates cache after update.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
        )
        pref, _ = NotificationPreference.objects.get_or_create(
            user=user,
            website=website,
        )
        for field, value in fields.items():
            setattr(pref, field, value)
        pref.save(update_fields=list(fields.keys()) + ['updated_at'])
        PreferenceService._invalidate_cache(user, website)

    @staticmethod
    def update_event_preference(
        user, website, event_key: str, **fields
    ) -> None:
        """Update a specific event preference for a user."""
        from notifications_system.models.notification_event import NotificationEvent
        from notifications_system.models.notification_preferences import (
            NotificationEventPreference,
        )

        event = NotificationEvent.objects.filter(
            event_key=event_key, is_active=True
        ).first()
        if not event:
            logger.warning(
                "update_event_preference() unknown event_key=%s.", event_key
            )
            return

        pref, _ = NotificationEventPreference.objects.get_or_create(
            user=user,
            website=website,
            event=event,
        )
        for field, value in fields.items():
            setattr(pref, field, value)
        pref.save(update_fields=list(fields.keys()) + ['updated_at'])
        PreferenceService._invalidate_cache(user, website)

    @staticmethod
    def reset_preferences(user, website) -> None:
        """
        Delete a user's preferences, reverting to system defaults.
        Also deletes per-event preferences.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
            NotificationEventPreference,
        )
        NotificationPreference.objects.filter(
            user=user, website=website
        ).delete()
        NotificationEventPreference.objects.filter(
            user=user, website=website
        ).delete()
        PreferenceService._invalidate_cache(user, website)
        logger.info(
            "Preferences reset for user=%s website=%s.",
            user.id,
            website.id,
        )

    # -------------------------
    # Cache helpers
    # -------------------------

    @staticmethod
    def _cache_key(user, website) -> str:
        website_id = getattr(website, 'id', 'none')
        return f"notif:pref:{user.id}:{website_id}"

    @staticmethod
    def _invalidate_cache(user, website) -> None:
        cache.delete(PreferenceService._cache_key(user, website))


    @staticmethod
    def get_cached_preference(user, website):
        """
        Return NotificationPreference from cache if available,
        otherwise fetch from DB and cache the PK.
        Creates default preference if none exists.
        """
        key = PreferenceService._cache_key(user, website)
        cached_pk = cache.get(key)

        if cached_pk:
            pref = NotificationPreference.objects.filter(pk=cached_pk).first()
            if pref:
                return pref
            # Cached PK is stale — fall through to DB fetch
            cache.delete(key)

        pref = PreferenceService.get_or_create_preference(user, website)

        if pref:
            # Cache PK only — never cache the ORM instance
            cache.set(key, pref.pk, timeout=PREF_CACHE_TTL)

        return pref


    @staticmethod
    def is_on_cooldown(user, website, event_key: str) -> bool:
        """
        Returns True if this event was recently sent to the user
        and is within the cooldown window.

        Cooldown period comes from NotificationEventConfig.cooldown_seconds.
        Falls back to 0 (no cooldown) if not configured.
        """
        from datetime import timedelta
        from notifications_system.models.event_config import NotificationEventConfig
        from notifications_system.models.notifications import Notification

        # Get cooldown from event config
        cooldown_secs = 0
        try:
            config = NotificationEventConfig.objects.get(
                event__event_key=event_key,
                is_active=True,
            )
            cooldown_secs = config.cooldown_seconds
        except NotificationEventConfig.DoesNotExist:
            pass

        if not cooldown_secs:
            return False

        cutoff = timezone.now() - timedelta(seconds=cooldown_secs)
        return Notification.objects.filter(
            user=user,
            website=website,
            event_key=event_key,
            created_at__gte=cutoff,
        ).exists()
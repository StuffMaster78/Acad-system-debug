"""Preference resolution and CRUD helpers.

This module focuses on determining effective notification preferences
for a user and managing default assignment/updates. Cache concerns are
delegated to `preferences_cache.py`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.core.cache import cache
import logging

from notifications_system.enums import NotificationType
from notifications_system.models.notification_preferences import (
    NotificationPreference,
)

logger = logging.getLogger(__name__)


class NotificationPreferenceResolver:
    """Resolve and manage a user's notification preferences.

    Resolution order (highest to lowest):
      1. Active group profile (if forced/override)
      2. Explicit user preference (per event)
      3. Role defaults (simple mapping)
      4. System default (in_app only)
    """

    # -------------------------
    # Resolution (read) methods
    # -------------------------

    @staticmethod
    def resolve(
        user,
        event: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        website=None,
    ) -> List[str]:
        """Return preferred channels for the user/event.

        Args:
            user: Authenticated user instance.
            event: Optional event key (e.g., "order.created").
            category: Optional category string (unused hook).
            priority: Optional priority label (unused hook).
            website: Tenant/site for multi-tenant setups.

        Returns:
            List of channel keys (e.g., ["in_app", "email"]).
        """
        del category, priority  # reserved hooks

        if not user or not getattr(user, "is_authenticated", False):
            return [NotificationType.IN_APP]

        # 1) Active group profile with force override
        gprof = getattr(user, "notification_group_profile", None)
        if gprof and getattr(gprof, "force_override", False):
            chans = list(getattr(gprof, "channels", []) or [])
            if chans:
                logger.debug("Group profile override applied for user %s", user)
                return chans

        # 2) User preference per event (if present)
        if event:
            try:
                pref = NotificationPreference.objects.get(
                    user=user, website=website
                )
                chans = pref.get_channels_for_event(event)  # your model helper
                if chans:
                    return list(chans)
            except NotificationPreference.DoesNotExist:
                pass

        # 3) Role defaults
        role = getattr(user, "role", None)
        role_defaults = {
            "writer": ["in_app", "email"],
            "client": ["email"],
            "editor": ["in_app"],
            "support": ["in_app", "email"],
            "admin": ["in_app", "email"],
        }
        if role in role_defaults:
            return role_defaults[role]

        # 4) System fallback
        return [NotificationType.IN_APP]

    @staticmethod
    def get_user_channel_order(user, event: Optional[str] = None) -> Optional[List[str]]:
        """Return a custom ordering of channels for the user/event.

        Assumes the model exposes:
            NotificationPreference.get_ordered_channels_for_event(event)

        Args:
            user: User instance.
            event: Optional event key.

        Returns:
            Ordered list of channels or None if unset.
        """
        try:
            pref = NotificationPreference.objects.get(
                user=user, website=getattr(user, "website", None)
            )
            return pref.get_ordered_channels_for_event(event)
        except NotificationPreference.DoesNotExist:
            return None

    # ------------------------
    # Defaults / seeding / CRUD
    # ------------------------

    @staticmethod
    def seed_user_event_preferences(user, website) -> None:
        """Seed per-event preference rows for a new user.

        Creates entries for all active events so later edits are simple.
        """
        from notifications_system.models.notification_event import (
            NotificationEvent,
        )
        from notifications_system.models.notification_preferences import (
            NotificationEventPreference,
        )

        for ev in NotificationEvent.objects.filter(is_active=True):
            NotificationEventPreference.objects.get_or_create(
                user=user, event=ev, website=website
            )

    @staticmethod
    def assign_default_preferences(user, website) -> NotificationPreference:
        """Create (or fetch) a user's default preference/profile.

        Selects a default NotificationProfile if present, then ensures
        the user has a NotificationPreference and seeded event rows.

        Args:
            user: User instance.
            website: Tenant/site instance.

        Returns:
            The user's NotificationPreference instance.
        """
        from notifications_system.models.notification_profile import (
            NotificationProfile,
        )

        default_prof = (
            NotificationProfile.objects.filter(name="Default").first()
            or NotificationProfile.objects.filter(is_active=True).first()
        )
        if not default_prof:
            raise ValueError("No default NotificationProfile found.")

        pref, created = NotificationPreference.objects.get_or_create(
            user=user, website=website, defaults={"profile": default_prof}
        )
        if created:
            NotificationPreferenceResolver.seed_user_event_preferences(
                user, website
            )
        return pref

    @staticmethod
    def update_user_preferences(
        user, preferences_data: Dict[str, Any]
    ) -> NotificationPreference:
        """Update a user's preferences and log the change.

        Args:
            user: User instance.
            preferences_data: Field->value updates for the preference row.

        Returns:
            The updated NotificationPreference instance.
        """
        from notifications_system.models.notification_log import (
            NotificationLog,
        )

        pref, _ = NotificationPreference.objects.get_or_create(
            user=user, website=getattr(user, "website", None)
        )
        before = {k: getattr(pref, k, None) for k in preferences_data.keys()}

        for field, value in preferences_data.items():
            setattr(pref, field, value)
        pref.save()

        NotificationLog.objects.create(
            notification=None,
            user=user,
            message="Preferences updated",
            channel="in_app",
            status="INFO",
            extra_data={"before": before, "after": preferences_data},
        )
        return pref

    # -----------------
    # Simple fetchers
    # -----------------

    @staticmethod
    def get_user_preferences(user) -> Optional[NotificationPreference]:
        """Return a user's NotificationPreference or None."""
        try:
            return NotificationPreference.objects.get(
                user=user, website=getattr(user, "website", None)
            )
        except NotificationPreference.DoesNotExist:
            return None

    @staticmethod
    def reset_user_preferences(user) -> bool:
        """Delete a user's preference row (reverts to defaults)."""
        try:
            pref = NotificationPreference.objects.get(
                user=user, website=getattr(user, "website", None)
            )
            pref.delete()
            return True
        except NotificationPreference.DoesNotExist:
            return False

    # -----------------
    # Cache utilities
    # -----------------

    @staticmethod
    def get_effective_preferences(user, website) -> Dict[str, Any]:
        """Return effective prefs (user/group/role/default), cached.

        Note:
            This returns a `dict` (flags per channel), not the model.
        """
        wid = getattr(website, "id", "none")
        key = f"notif_prefs:{user.id}:{wid}"
        cached = cache.get(key)
        if cached:
            return cached

        # 1) User-level
        try:
            pref = NotificationPreference.objects.get(
                user=user, website=website
            )
            result = pref.as_dict()  # model should expose this
            cache.set(key, result, timeout=3600)
            return result
        except NotificationPreference.DoesNotExist:
            pass

        # 2) Group-level
        group = getattr(user, "groups", None)
        group = group.first() if group else None
        if group:
            from notifications_system.models.notification_profile import (
                NotificationGroupProfile,
            )

            gprof = NotificationGroupProfile.objects.filter(
                group=group, website=website, is_active=True
            ).first()
            if gprof:
                result = gprof.as_dict()
                cache.set(key, result, timeout=3600)
                return result

        # 3) Role-level
        role_slug = getattr(getattr(user, "role", None), "slug", None)
        if role_slug:
            from notifications_system.models.notification_profile import (
                NotificationGroupProfile,
            )

            rprof = NotificationGroupProfile.objects.filter(
                role_slug=role_slug, website=website, is_active=True
            ).first()
            if rprof:
                result = rprof.as_dict()
                cache.set(key, result, timeout=3600)
                return result

        # 4) Global default
        from notifications_system.models.notification_profile import (
            NotificationProfile,
        )

        default = NotificationProfile.objects.filter(is_default=True).first()
        if default:
            result = {
                "receive_email": default.receive_email,
                "receive_in_app": default.receive_in_app,
                "receive_push": default.receive_push,
                "receive_sms": default.receive_sms,
                "source": "global",
            }
            cache.set(key, result, timeout=3600)
            return result

        # Hard fallback
        result = {
            "receive_email": True,
            "receive_in_app": True,
            "receive_push": False,
            "receive_sms": False,
            "source": "fallback",
        }
        cache.set(key, result, timeout=3600)
        return result

    @staticmethod
    def update_preferences_cache(user) -> None:
        """Refresh a user's cached effective preferences."""
        website = getattr(user, "website", None)
        wid = getattr(website, "id", "none")
        key = f"notif_prefs:{user.id}:{wid}"

        try:
            pref = NotificationPreference.objects.get(
                user=user, website=website
            )
            cache.set(key, pref.as_dict(), timeout=3600)
        except NotificationPreference.DoesNotExist:
            cache.delete(key)
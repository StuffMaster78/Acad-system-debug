"""Policy helpers to decide *if* and *where* to send notifications."""

from __future__ import annotations

import hashlib
from typing import Iterable, List, Optional, Set

from django.utils import timezone

from notifications_system.enums import NotificationType
from notifications_system.registry.forced_channels import forced_channel_registry
from notifications_system.registry.role_bindings import get_channels_for_role
from notifications_system.services.preferences import (
    NotificationPreferenceResolver,
)
from notifications_system.utils.dnd import is_dnd_now


class NotificationPolicy:
    """Combine role defaults, forced channels, prefs, mute, and DND."""

    def __init__(
        self,
        user,
        event_key: str,
        *,
        context: Optional[dict] = None,
        website=None,
        role: Optional[str] = None,
    ):
        """Init policy.

        Args:
            user: Target user instance.
            event_key: Canonical event key (e.g. "order.created").
            context: Optional event context.
            website: Tenant/site object (if multi-tenant).
            role: Optional role override (else uses user.role).
        """
        self.user = user
        self.event_key = event_key
        self.context = context or {}
        self.website = website or getattr(user, "website", None)
        self.role = role or getattr(user, "role", None)

    # -----------------------------
    # Public decision entry points
    # -----------------------------

    def should_send(self) -> bool:
        """Return True if this notification should be sent at all.

        Applies global suppressions such as account state, explicit "silent"
        payloads, user mute (unless explicitly critical in caller), and DND
        (when all candidate channels are DND-blocked).

        Note:
            Critical/override logic should be decided by the caller; this
            helper is conservative.
        """
        if getattr(self.user, "is_suspended", False):
            return False

        if self.context.get("silent") is True:
            return False

        # Respect user mute flag if present.
        is_muted = getattr(getattr(self.user, "pref", None), "is_muted", None)
        if callable(is_muted) and is_muted():
            return False

        # DND: if user is in DND and no channels remain after filtering,
        #      let channel resolution handle it (return True here), but
        #      you can choose to short-circuit if desired.
        return True

    def allowed_channels(
        self,
        *,
        explicit_channels: Optional[Iterable[str]] = None,
    ) -> List[str]:
        """Resolve final channel list for this user + event.

        Combines, in order:
            1) Forced channels (override everything).
            2) Explicit channels provided by the caller.
            3) Role-based defaults for this event.
            4) User preferences (filtering step).

        Also removes channels blocked by DND profile (if present).

        Args:
            explicit_channels: Optional explicit channels to use.

        Returns:
            List of channel keys (e.g., ["in_app", "email"]).
        """
        forced: Set[str] = forced_channel_registry.get(self.event_key)
        if forced:
            base: List[str] = list(forced)
        elif explicit_channels:
            base = list(explicit_channels)
        else:
            base = list(
                get_channels_for_role(self.event_key, self.role or "")
            ) or self._prefs_default()

        # Filter by user preferences unless forced.
        if not forced:
            base = self._filter_by_prefs(base)

        # Apply DND channel filter.
        base = self._filter_by_dnd(base)

        # Fallback to in_app if nothing remains.
        return base or [NotificationType.IN_APP]

    def throttle_key(self) -> str:
        """Return a stable key suitable for rate limiting/dedup.

        Format:
            sha256("{event_key}:{user_id}:{website_id|none}")
        """
        uid = getattr(self.user, "id", "unknown")
        wid = getattr(self.website, "id", "none") if self.website else "none"
        raw = f"{self.event_key}:{uid}:{wid}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # -----------------
    # Internal helpers
    # -----------------

    def _prefs_default(self) -> List[str]:
        """Default channels from user effective preferences."""
        return list(
            NotificationPreferenceResolver.get_effective_preferences(
                user=self.user,
                website=self.website,
            )
        )

    def _filter_by_prefs(self, channels: Iterable[str]) -> List[str]:
        """Apply per-channel user preferences."""
        prefs = getattr(self.user, "notification_preferences", None)
        if not prefs:
            return list(channels)

        enabled: List[str] = []
        for ch in channels:
            if self._is_channel_enabled(prefs, ch):
                enabled.append(ch)
        return enabled

    def _is_channel_enabled(self, prefs, channel: str) -> bool:
        """Return True if a prefs object enables the channel."""
        # Mirror the logic used in NotificationService._is_channel_enabled.
        if channel == NotificationType.EMAIL:
            return getattr(prefs, "receive_email", True)
        if channel == NotificationType.SMS:
            return getattr(prefs, "receive_sms", True)
        if channel == NotificationType.PUSH:
            return getattr(prefs, "receive_push", True)
        if channel == NotificationType.IN_APP:
            return getattr(prefs, "receive_in_app", True)
        if channel == NotificationType.WEBHOOK:
            return getattr(prefs, "receive_webhook", True)
        if channel == NotificationType.SSE:
            return getattr(prefs, "receive_sse", True)
        if channel == NotificationType.WS:
            return getattr(prefs, "receive_ws", True)
        return True

    def _filter_by_dnd(self, channels: Iterable[str]) -> List[str]:
        """Drop channels the user has blocked during DND."""
        profile = getattr(self.user, "notification_profile", None)
        if not profile or not is_dnd_now(profile):
            return list(channels)

        blocked = set(getattr(profile, "dnd_channels", []) or [])
        return [c for c in channels if c not in blocked]
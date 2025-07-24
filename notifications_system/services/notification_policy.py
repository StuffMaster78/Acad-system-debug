from notifications_system.enums import NotificationChannel
from notifications_system.models.notification_preferences import (
    NotificationPreference
)
from notifications_system.services.preferences import NotificationPreferenceResolver
from django.utils.timezone import now
import hashlib

class NotificationPolicy:
    def __init__(self, user, event_key, *, context=None, website=None):
        self.user = user
        self.event_key = event_key
        self.website = website or getattr(user, "website", None)
        self.context = context or {}
        self.priority = self.context.get("priority", "normal")

    def get_allowed_channels(self) -> list[str]:
        """
        Combines role-based defaults, user preferences, and forced overrides.
        """
        role_channels = self._get_role_based_defaults()
        forced_channels = self._get_forced_channels()
        user_prefs = NotificationPreferenceResolver.get_effective_preferences(
            self.user, self.website
        )

        allowed = []
        for channel in set(role_channels + forced_channels):
            # Allow if explicitly opted in OR if forced
            if channel in forced_channels or user_prefs.is_enabled(channel, self.event_key):
                allowed.append(channel)

        return allowed

    def should_send(self) -> bool:
        """
        Should this notification even be sent?
        Useful for global suppression,
        user DND, account state, or quiet hours.
        """
        if getattr(self.user, "is_suspended", False):
            return False

        if self.context.get("silent") is True:
            return False

        return True

    def get_throttle_key(self) -> str:
        """
        Used for deduplication or rate-limiting logic.
        Can be plugged into Redis or DB-level suppression logic.
        """
        key_string = f"{self.event_key}:{self.user.id}:{self.website.id if self.website else 'none'}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    # --- Private Helpers ---

    def _get_role_based_defaults(self) -> list[str]:
        """
        Return default channels based on role/event.
        These are the channels we'd send to unless overridden.
        """
        role = getattr(self.user, "role", None)
        if role == "writer":
            return [
                NotificationChannel.EMAIL, NotificationChannel.IN_APP,
                NotificationChannel.DISCORD, NotificationChannel.WEBSOCKET,
                NotificationChannel.SMS, NotificationChannel.PUSH,
                NotificationChannel.TELEGRAM
            ]
        elif role == "client":
            return [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
        elif role == "admin":
            return [NotificationChannel.EMAIL, NotificationChannel.IN_APP, NotificationChannel.TELEGRAM]
        return [NotificationChannel.IN_APP]

    def _get_forced_channels(self) -> list[str]:
        """
        For critical events, we can enforce specific channels.
        """
        forced = {
            "order_assigned": [NotificationChannel.DISCORD],
            "payment_failed": [NotificationChannel.EMAIL, NotificationChannel.SMS],
            "security_alert": [NotificationChannel.EMAIL, NotificationChannel.TELEGRAM],
        }
        return forced.get(self.event_key, [])
import logging
from users.models import UserRole
from notifications_system.models import (
    NotificationPreference,
    NotificationGroupProfile,
    BroadcastNotification
)
from notifications_system.enums import NotificationType

logger = logging.getLogger(__name__)

class NotificationPreferenceResolver:
    @staticmethod
    def resolve(user, event=None, category=None, priority=None, website=None):
        """
        Determines preferred delivery channels for a user for a given event/category.

        Fallback order:
        1. Group Profile (if user assigned one)
        2. User Preference (per event or channel)
        3. Role-based Default (e.g. Writers → Aggressive)
        4. System Default (in_app only)
        """
        if not user or not user.is_authenticated:
            return [NotificationType.IN_APP]

        # 1. Apply active group profile if any
        if hasattr(user, "notification_group_profile") and user.notification_group_profile:
            group_profile = user.notification_group_profile
            if group_profile.force_override:
                logger.debug(f"Group profile override for {user}")
                return group_profile.channels

        # 2. User Preferences per event
        if event:
            pref = NotificationPreference.objects.filter(
                user=user, event=event
            ).first()
            if pref:
                return pref.channels

        # 3. Role-based Defaults
        role = getattr(user, "role", None)
        if role:
            default_map = {
                UserRole.WRITER: ["in_app", "email"],
                UserRole.CLIENT: ["email"],
                UserRole.EDITOR: ["in_app"],
                UserRole.SUPPORT: ["in_app", "email"],
                UserRole.ADMIN: ["in_app", "email"],
            }
            return default_map.get(role, ["in_app"])

        # 4. Fallback
        return ["in_app"]
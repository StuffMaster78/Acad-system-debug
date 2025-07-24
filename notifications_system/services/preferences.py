from django.core.cache import cache
from django.db import models
import logging
from users.mixins import UserRole

from notifications_system.models.notification_preferences import (
    NotificationPreference,
)
from notifications_system.models.notification_event import (
    NotificationEvent
)
from notifications_system.models.notification_profile import (
    NotificationProfile,
    NotificationGroupProfile,
)
from notifications_system.models.broadcast_notification import (
    BroadcastNotification,
)
from notifications_system.models.notification_log import (
    NotificationLog,
)
from notifications_system.enums import (
    NotificationType,
    NotificationPriority
)
from django.core.cache import cache
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)

class NotificationPreferenceResolver:
    """
    Resolves notification preferences for a user based on various criteria.
    Fallback order:
    1. Group Profile (if user assigned one)
    2. User Preference (per event or channel)
    3. Role-based Default (e.g. Writers → Aggressive)
    4. System Default (in_app only)
    """
    @staticmethod
    def resolve(
            user, event=None, category=None,
            priority=None, website=None
    ):
            """
            Determines preferred delivery channels for a 
            user for a given event/category.

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
    @staticmethod
    def get_user_channel_order(user, event=None):
        # This assumes NotificationPreference has a list field: preferred_channels
        try:
            pref = NotificationPreference.objects.get(user=user)
            return pref.get_ordered_channels_for_event(event)
        except NotificationPreference.DoesNotExist:
            return None
        
    @staticmethod
    def seed_user_event_preferences(user, website):
        """
        Seeds default event preferences for a user.
        This is typically called when a new user is created.
        It ensures that the user has preferences set for all active events.
        """
        from notifications_system.models.notification_event import (
            NotificationEvent
        )
        from notifications_system.models.notification_preferences import (
            NotificationEventPreference
        )
        events = NotificationEvent.objects.filter(is_active=True)

        for event in events:
            NotificationEventPreference.objects.get_or_create(
                user=user,
                event=event,
                website=website,
            )

    def assign_default_preferences(user, website):
        """Assign default notification preferences for a user."""
        from notifications_system.models.notification_profile import (
            NotificationProfile
        )
        from notifications_system.models.notification_preferences import (
            NotificationPreference
        )

        # Assign default notification profile
        default_profile = NotificationProfile.objects.filter(name="Default").first()
        if not default_profile:
            raise ValueError("Default notification profile not found.")

        # Create notification preference with the default profile
        preference, created = NotificationPreference.objects.get_or_create(
            user=user,
            website=website,
            defaults={'profile': default_profile}
        )

        if created:
            NotificationPreferenceResolver.seed_user_event_preferences(user, website)

        return preference

    def update_user_preferences(user, preferences_data):
        """
        Update user notification preferences based on provided data.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference
        )

        preference, created = NotificationPreference.objects.get_or_create(
            user=user, website=user.website
        )

        before = preference.__dict__.copy()

        for field, value in preferences_data.items():
            setattr(preference, field, value)

        preference.save()

        NotificationLog.objects.create(
            notification=None,
            user=user,
            message=f"Preferences updated",
            channel="in_app",
            status="INFO",
            extra_data={"before": before, "after": preferences_data}
        )

        return preference


    def get_user_preferences(user):
        """
        Retrieve the notification preferences for a user.
        If no preferences exist, return None.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference
        )

        try:
            preference = NotificationPreference.objects.get(
                user=user, website=user.website
            )
            return preference
        except NotificationPreference.DoesNotExist:
            return None
        
    def reset_user_preferences(user):
        """"Reset user notification preferences to default."""
        from notifications_system.models.notification_preferences import (
            NotificationPreference
        )

        try:
            preference = NotificationPreference.objects.get(
                user=user, website=user.website
            )
            preference.delete()
            return True
        except NotificationPreference.DoesNotExist:
            return False
        

    def get_default_notification_profile():
        """"Get the default notification profile of the user."""
        from notifications_system.models.notification_profile import (
            NotificationProfile
        )

        try:
            return NotificationProfile.objects.get(is_default=True)
        except NotificationProfile.DoesNotExist:
            return None
        

    def get_notification_profiles():
        """"Get all notification profiles."""
        from notifications_system.models.notification_profile import (
            NotificationProfile
        )

        return NotificationProfile.objects.all().order_by('name')


    def get_notification_preferences(user):
        """Retrieve the notification preferences for a user.
        If no preferences exist, return None.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference
        )

        try:
            return NotificationPreference.objects.get(user=user, website=user.website)
        except NotificationPreference.DoesNotExist:
            return None
        

    def get_notification_preferences_by_profile(profile):
        """Retrieve notification preferences by profile.
        If no preferences exist, return an empty queryset.
        Example usage:
        >>> profile = NotificationProfile.objects.get(name="Default")
        >>> preferences = get_notification_preferences_by_profile(profile)
        :param profile: NotificationProfile instance
        :return: QuerySet of NotificationPreference objects
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference
        )

        return NotificationPreference.objects.filter(profile=profile).order_by('user__username')


    def get_cached_user_preferences(user):
        """"Get cached user notification preferences."""
        cache_key = f"notif_prefs:{user.id}"
        prefs = cache.get(cache_key)
        if not prefs:
            prefs = NotificationPreference.objects.filter(
                user=user, website=user.website
            ).first()
            if prefs:
                cache.set(cache_key, prefs, timeout=300)
        return prefs

    def rebuild_user_preferences_cache(user):
        """"Rebuild user notification preferences cache."""
        from notifications_system.models.notification_preferences import (
            NotificationPreference
        )

        cache_key = f"notif_prefs:{user.id}"
        prefs = NotificationPreference.objects.filter(
            user=user, website=user.website
        ).first()
        if prefs:
            cache.set(cache_key, prefs, timeout=300)
        else:
            cache.delete(cache_key)  # Clear cache if no preferences found


    def clear_user_preferences_cache(user):
        """Clear the cache for user notification preferences."""
        cache_key = f"notif_prefs:{user.id}"
        cache.delete(cache_key)
        return True

    def clear_all_preferences_cache():
        """Clear the cache for all user notification preferences."""
        from django.core.cache import cache

        cache.clear()
        return True


    def get_broadcast_notifications(website=None):
        """Retrieve broadcast notifications."""
        from notifications_system.models.broadcast_notification import (
            BroadcastNotification
        )

        if website:
            return BroadcastNotification.objects.filter(website=website).order_by('-created_at')
        return BroadcastNotification.objects.all().order_by('-created_at')

    def get_broadcast_notification_by_id(notification_id, website=None):
        """"Retrieve a specific broadcast notification by ID."""
        from notifications_system.models.broadcast_notification import BroadcastNotification

        if website:
            return BroadcastNotification.objects.filter(id=notification_id, website=website).first()
        return BroadcastNotification.objects.filter(id=notification_id).first()

    def get_notification_log(user=None, notification=None):
        from notifications_system.models.notification_log import NotificationLog

        if user:
            return NotificationLog.objects.filter(user=user).order_by('-created_at')
        elif notification:
            return NotificationLog.objects.filter(notification=notification).order_by('-created_at')
        return NotificationLog.objects.all().order_by('-created_at')

    def get_notification_profile(user):
        from notifications_system.models.notification_profile import NotificationProfile

        try:
            return NotificationProfile.objects.get(user=user, website=user.website)
        except NotificationProfile.DoesNotExist:
            return None
        
    def get_notification_group_profile(user):
        from notifications_system.models.notification_profile import NotificationGroupProfile

        try:
            return NotificationGroupProfile.objects.get(user=user, website=user.website)
        except NotificationGroupProfile.DoesNotExist:
            return None
        


    def get_effective_preferences(user, website):
        """
        Get effective notification preferences for a user.
        This checks user-level, group-level, role-level
        """
        cache_key = f"notif_prefs:{user.id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # 1. User-level
        try:
            pref = NotificationPreference.objects.get(
                user=user, website=website
            )
            cache.set(cache_key, pref.as_dict(), timeout=3600)
            return pref.as_dict()
        except NotificationPreference.DoesNotExist:
            pass

        # 2. Group-level
        group = user.groups.first()
        if group:
            group_profile = NotificationGroupProfile.objects.filter(
                group=group, website=website, is_active=True
            ).first()
            if group_profile:
                result = group_profile.as_dict()
                cache.set(cache_key, result, timeout=3600)
                return result

        # 3. Role-level
        role_slug = getattr(getattr(user, "role", None), "slug", None)
        if role_slug:
            role_profile = NotificationGroupProfile.objects.filter(
                role_slug=role_slug, website=website, is_active=True
            ).first()
            if role_profile:
                result = role_profile.as_dict()
                cache.set(cache_key, result, timeout=3600)
                return result

        # 4. Global fallback
        default = NotificationProfile.objects.filter(is_default=True).first()
        if default:
            result = {
                "receive_email": default.receive_email,
                "receive_in_app": default.receive_in_app,
                "receive_push": default.receive_push,
                "receive_sms": default.receive_sms,
                "source": "global"
            }
            cache.set(cache_key, result, timeout=3600)
            return result

        return {
            "receive_email": True,
            "receive_in_app": True,
            "receive_push": False,
            "receive_sms": False,
            "source": "fallback"
        }

    def update_preferences_cache(user):
        """
        Rebuilds the cache for user notification preferences.
        """
        cache_key = f"notif_prefs:{user.id}"
        prefs = NotificationPreference.objects.filter(user=user, website=user.website).first()
        if prefs:
            cache.set(cache_key, prefs.as_dict(), timeout=3600)
        else:
            cache.delete(cache_key)  # Clear cache if no preferences found
"""
Service for managing notification preference profiles.
Handles business logic for creating, updating, and applying notification profiles.
"""
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import List, Dict, Optional, Set
from websites.models import Website

from notifications_system.models.notification_preferences import (
    NotificationPreferenceProfile,
    NotificationPreference,
    EventNotificationPreference,
)
from notifications_system.enums import (
    NotificationType,
    EventType,
    OrderEvent,
    TicketEvent,
    WalletEvent,
    AccountEvent,
    MessageEvent,
    WriterEvent,
    PayoutEvent,
    FileEvent,
)

User = get_user_model()


class NotificationProfileService:
    """Service for managing notification preference profiles."""
    
    @staticmethod
    def create_profile(
        name: str,
        description: str = "",
        website: Optional[Website] = None,
        default_email: bool = True,
        default_sms: bool = False,
        default_push: bool = False,
        default_in_app: bool = True,
        email_enabled: bool = True,
        sms_enabled: bool = False,
        push_enabled: bool = False,
        in_app_enabled: bool = True,
        dnd_enabled: bool = False,
        dnd_start_hour: int = 22,
        dnd_end_hour: int = 6,
        is_default: bool = False,
    ) -> NotificationPreferenceProfile:
        """
        Create a new notification preference profile.
        
        Args:
            name: Profile name (must be unique)
            description: Profile description
            website: Optional website association
            default_email: Default email setting
            default_sms: Default SMS setting
            default_push: Default push setting
            default_in_app: Default in-app setting
            email_enabled: Email enabled
            sms_enabled: SMS enabled
            push_enabled: Push enabled
            in_app_enabled: In-app enabled
            dnd_enabled: Do-not-disturb enabled
            dnd_start_hour: DND start hour (0-23)
            dnd_end_hour: DND end hour (0-23)
            is_default: Whether this is the default profile
            
        Returns:
            Created NotificationPreferenceProfile instance
        """
        # If setting as default, unset other defaults
        if is_default:
            NotificationPreferenceProfile.objects.filter(
                is_default=True,
                website=website
            ).update(is_default=False)
        
        profile = NotificationPreferenceProfile.objects.create(
            name=name,
            description=description,
            website=website,
            default_email=default_email,
            default_sms=default_sms,
            default_push=default_push,
            default_in_app=default_in_app,
            email_enabled=email_enabled,
            sms_enabled=sms_enabled,
            push_enabled=push_enabled,
            in_app_enabled=in_app_enabled,
            dnd_enabled=dnd_enabled,
            dnd_start_hour=dnd_start_hour,
            dnd_end_hour=dnd_end_hour,
            is_default=is_default,
        )
        
        return profile
    
    @staticmethod
    def update_profile(
        profile: NotificationPreferenceProfile,
        **kwargs
    ) -> NotificationPreferenceProfile:
        """
        Update a notification preference profile.
        
        Args:
            profile: Profile instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated NotificationPreferenceProfile instance
        """
        # If setting as default, unset other defaults
        if kwargs.get('is_default') is True:
            NotificationPreferenceProfile.objects.filter(
                is_default=True,
                website=profile.website
            ).exclude(id=profile.id).update(is_default=False)
        
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.save()
        return profile
    
    @staticmethod
    @transaction.atomic
    def apply_profile_to_user(
        profile: NotificationPreferenceProfile,
        user: User,
        website: Optional[Website] = None,
        override_existing: bool = False
    ) -> Dict[str, any]:
        """
        Apply a notification profile to a user.
        Creates or updates user notification preferences based on the profile.
        
        Args:
            profile: Profile to apply
            user: User to apply profile to
            website: Website context (uses profile's website if not provided)
            override_existing: Whether to override existing preferences
            
        Returns:
            Dict with applied preferences count and details
        """
        if not website:
            website = profile.website
        
        if not website:
            raise ValueError("Website is required to apply profile")
        
        applied_count = 0
        updated_count = 0
        created_count = 0
        
        # Get all available events
        all_events = NotificationProfileService._get_all_events()
        
        # Apply profile settings to user preferences
        for event_key in all_events:
            # Determine channel settings based on profile
            email_enabled = profile.email_enabled and profile.default_email
            sms_enabled = profile.sms_enabled and profile.default_sms
            push_enabled = profile.push_enabled and profile.default_push
            in_app_enabled = profile.in_app_enabled and profile.default_in_app
            
            # Create or update EventNotificationPreference
            event_pref, created = EventNotificationPreference.objects.update_or_create(
                user=user,
                event=event_key,
                website=website,
                defaults={
                    'email_enabled': email_enabled,
                    'sms_enabled': sms_enabled,
                    'push_enabled': push_enabled,
                    'in_app_enabled': in_app_enabled,
                    'dnd_enabled': profile.dnd_enabled,
                    'dnd_start': profile.dnd_start_hour,
                    'dnd_end': profile.dnd_end_hour,
                }
            )
            
            if created:
                created_count += 1
            else:
                if override_existing:
                    updated_count += 1
                else:
                    continue
            
            applied_count += 1
        
        return {
            'profile_id': profile.id,
            'profile_name': profile.name,
            'user_id': user.id,
            'user_email': user.email,
            'website_id': website.id,
            'total_events': len(all_events),
            'applied_count': applied_count,
            'created_count': created_count,
            'updated_count': updated_count,
        }
    
    @staticmethod
    @transaction.atomic
    def apply_profile_to_users(
        profile: NotificationPreferenceProfile,
        user_ids: List[int],
        website: Optional[Website] = None,
        override_existing: bool = False
    ) -> Dict[str, any]:
        """
        Apply a notification profile to multiple users.
        
        Args:
            profile: Profile to apply
            user_ids: List of user IDs
            website: Website context
            override_existing: Whether to override existing preferences
            
        Returns:
            Dict with summary of applied profiles
        """
        users = User.objects.filter(id__in=user_ids)
        results = []
        
        for user in users:
            try:
                result = NotificationProfileService.apply_profile_to_user(
                    profile=profile,
                    user=user,
                    website=website,
                    override_existing=override_existing
                )
                results.append(result)
            except Exception as e:
                results.append({
                    'user_id': user.id,
                    'user_email': user.email,
                    'error': str(e)
                })
        
        return {
            'profile_id': profile.id,
            'profile_name': profile.name,
            'total_users': len(user_ids),
            'successful': len([r for r in results if 'error' not in r]),
            'failed': len([r for r in results if 'error' in r]),
            'results': results,
        }
    
    @staticmethod
    def get_profile_statistics(profile: NotificationPreferenceProfile) -> Dict[str, any]:
        """
        Get statistics about a notification profile.
        
        Args:
            profile: Profile to get statistics for
            
        Returns:
            Dict with profile statistics
        """
        # Count users with this profile applied
        # (This would require tracking which users have which profile)
        # For now, we'll return basic profile info
        
        return {
            'profile_id': profile.id,
            'profile_name': profile.name,
            'is_default': profile.is_default,
            'channels_enabled': {
                'email': profile.email_enabled,
                'sms': profile.sms_enabled,
                'push': profile.push_enabled,
                'in_app': profile.in_app_enabled,
            },
            'dnd_enabled': profile.dnd_enabled,
            'dnd_hours': f"{profile.dnd_start_hour}:00 - {profile.dnd_end_hour}:00" if profile.dnd_enabled else None,
            'website': profile.website.name if profile.website else None,
        }
    
    @staticmethod
    def _get_all_events() -> List[str]:
        """
        Get all available notification event keys.
        
        Returns:
            List of event keys
        """
        events = []
        
        # Add all event types from enums
        events.extend(OrderEvent.values)
        events.extend(TicketEvent.values)
        events.extend(WalletEvent.values)
        events.extend(AccountEvent.values)
        events.extend(MessageEvent.values)
        events.extend(WriterEvent.values)
        events.extend(PayoutEvent.values)
        events.extend(FileEvent.values)
        
        return events
    
    @staticmethod
    def duplicate_profile(
        source_profile: NotificationPreferenceProfile,
        new_name: str,
        website: Optional[Website] = None
    ) -> NotificationPreferenceProfile:
        """
        Duplicate a notification profile with a new name.
        
        Args:
            source_profile: Profile to duplicate
            new_name: Name for the new profile
            website: Website for the new profile (uses source if not provided)
            
        Returns:
            New NotificationPreferenceProfile instance
        """
        if not website:
            website = source_profile.website
        
        return NotificationPreferenceProfile.objects.create(
            name=new_name,
            description=f"Copied from {source_profile.name}",
            website=website,
            default_email=source_profile.default_email,
            default_sms=source_profile.default_sms,
            default_push=source_profile.default_push,
            default_in_app=source_profile.default_in_app,
            email_enabled=source_profile.email_enabled,
            sms_enabled=source_profile.sms_enabled,
            push_enabled=source_profile.push_enabled,
            in_app_enabled=source_profile.in_app_enabled,
            dnd_enabled=source_profile.dnd_enabled,
            dnd_start_hour=source_profile.dnd_start_hour,
            dnd_end_hour=source_profile.dnd_end_hour,
            is_default=False,  # Don't duplicate default status
        )


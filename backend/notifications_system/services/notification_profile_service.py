"""
notifications_system/services/notification_profile_service.py

Manages notification preference profiles — creation, updating,
applying to users, duplication, and statistics.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)


class NotificationProfileService:
    """
    Manages NotificationPreferenceProfile lifecycle and application.
    Profiles are admin-created templates applied to users or roles.
    """

    @staticmethod
    def create_profile(
        name: str,
        website,
        description: str = '',
        email_enabled: bool = True,
        in_app_enabled: bool = True,
        dnd_enabled: bool = False,
        dnd_start_hour: int = 22,
        dnd_end_hour: int = 6,
        digest_enabled: bool = False,
        digest_frequency: str = 'daily',
        is_default: bool = False,
        created_by=None,
    ):
        """
        Create a new notification preference profile.
        If is_default is True, demotes any existing default for this website.

        Returns:
            NotificationPreferenceProfile instance
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )

        with transaction.atomic():
            if is_default:
                NotificationPreferenceProfile.objects.filter(
                    website=website,
                    is_default=True,
                ).update(is_default=False)

            return NotificationPreferenceProfile.objects.create(
                name=name,
                description=description,
                website=website,
                email_enabled=email_enabled,
                in_app_enabled=in_app_enabled,
                dnd_enabled=dnd_enabled,
                dnd_start_hour=dnd_start_hour,
                dnd_end_hour=dnd_end_hour,
                digest_enabled=digest_enabled,
                digest_frequency=digest_frequency,
                is_default=is_default,
                created_by=created_by,
            )

    @staticmethod
    def update_profile(profile, **kwargs):
        """
        Update fields on a profile.
        Handles default demotion if is_default is being set to True.

        Returns:
            Updated NotificationPreferenceProfile instance
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )

        with transaction.atomic():
            if kwargs.get('is_default') is True:
                NotificationPreferenceProfile.objects.filter(
                    website=profile.website,
                    is_default=True,
                ).exclude(pk=profile.pk).update(is_default=False)

            for field, value in kwargs.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)

            profile.save()
            return profile

    @staticmethod
    def duplicate_profile(
        source_profile,
        new_name: str,
        website=None,
    ):
        """
        Duplicate a profile with a new name.
        Duplicated profile is never marked as default.

        Returns:
            New NotificationPreferenceProfile instance
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreferenceProfile,
        )

        return NotificationPreferenceProfile.objects.create(
            name=new_name,
            description=f"Copied from {source_profile.name}",
            website=website or source_profile.website,
            email_enabled=source_profile.email_enabled,
            in_app_enabled=source_profile.in_app_enabled,
            dnd_enabled=source_profile.dnd_enabled,
            dnd_start_hour=source_profile.dnd_start_hour,
            dnd_end_hour=source_profile.dnd_end_hour,
            digest_enabled=source_profile.digest_enabled,
            digest_frequency=source_profile.digest_frequency,
            is_default=False,
        )

    @staticmethod
    @transaction.atomic
    def apply_profile_to_user(
        profile,
        user,
        website=None,
        override_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        Apply a profile to a single user.
        Updates the user's NotificationPreference and per-event preferences.

        Args:
            profile:           Profile to apply
            user:              User to apply to
            website:           Website context — uses profile.website if not given
            override_existing: If False, skips events with existing preferences

        Returns:
            Summary dict with counts
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
            NotificationEventPreference,
        )
        from notifications_system.models.notification_event import NotificationEvent

        website = website or profile.website
        if not website:
            raise ValueError("Website is required to apply a profile.")

        # Update or create master preference
        pref, _ = NotificationPreference.objects.update_or_create(
            user=user,
            website=website,
            defaults={
                'profile': profile,
                'email_enabled': profile.email_enabled,
                'in_app_enabled': profile.in_app_enabled,
                'dnd_enabled': profile.dnd_enabled,
                'dnd_start_hour': profile.dnd_start_hour,
                'dnd_end_hour': profile.dnd_end_hour,
                'digest_enabled': profile.digest_enabled,
                'digest_frequency': profile.digest_frequency,
            },
        )

        # Apply to per-event preferences
        active_events = NotificationEvent.objects.filter(is_active=True)
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for event in active_events:
            event_pref, created = NotificationEventPreference.objects.get_or_create(
                user=user,
                website=website,
                event=event,
                defaults={
                    'email_enabled': profile.email_enabled,
                    'in_app_enabled': profile.in_app_enabled,
                    'is_enabled': True,
                },
            )

            if created:
                created_count += 1
            elif override_existing:
                event_pref.email_enabled = profile.email_enabled
                event_pref.in_app_enabled = profile.in_app_enabled
                event_pref.save(update_fields=[
                    'email_enabled', 'in_app_enabled', 'updated_at'
                ])
                updated_count += 1
            else:
                skipped_count += 1

        logger.info(
            "apply_profile_to_user: profile=%s user=%s website=%s "
            "created=%s updated=%s skipped=%s.",
            profile.id, user.id, website.id,
            created_count, updated_count, skipped_count,
        )

        return {
            'profile_id': profile.id,
            'profile_name': profile.name,
            'user_id': user.id,
            'website_id': website.id,
            'created_count': created_count,
            'updated_count': updated_count,
            'skipped_count': skipped_count,
        }

    @staticmethod
    def apply_profile_to_users(
        profile,
        user_ids: List[int],
        website=None,
        override_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        Apply a profile to multiple users.
        Each user is processed independently — one failure doesn't
        roll back others.

        Returns:
            Summary dict with per-user results
        """
        User = settings.AUTH_USER_MODEL

        users = User.objects.filter(id__in=user_ids, is_active=True)
        results = []
        failed = 0

        for user in users:
            try:
                result = NotificationProfileService.apply_profile_to_user(
                    profile=profile,
                    user=user,
                    website=website,
                    override_existing=override_existing,
                )
                results.append(result)
            except Exception as exc:
                failed += 1
                logger.error(
                    "apply_profile_to_users failed for user=%s: %s",
                    user.id,  # type: ignore[attr-defined]
                    exc,
                )
                results.append({
                    'user_id': user.id,  # type: ignore[attr-defined]
                    'error': str(exc),
                })

        return {
            'profile_id': profile.id,
            'profile_name': profile.name,
            'total_users': len(user_ids),
            'successful': len(results) - failed,
            'failed': failed,
            'results': results,
        }

    @staticmethod
    def get_profile_statistics(profile) -> Dict[str, Any]:
        """
        Return statistics for a profile including user adoption count.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
        )

        users_with_profile = NotificationPreference.objects.filter(
            profile=profile,
        ).count()

        return {
            'profile_id': profile.id,
            'profile_name': profile.name,
            'website': profile.website.name if profile.website else 'Global',
            'is_default': profile.is_default,
            'channels': {
                'email': profile.email_enabled,
                'in_app': profile.in_app_enabled,
            },
            'dnd_enabled': profile.dnd_enabled,
            'dnd_hours': (
                f"{profile.dnd_start_hour}:00 — {profile.dnd_end_hour}:00"
                if profile.dnd_enabled else None
            ),
            'digest_enabled': profile.digest_enabled,
            'digest_frequency': profile.digest_frequency,
            'users_with_profile': users_with_profile,
        }
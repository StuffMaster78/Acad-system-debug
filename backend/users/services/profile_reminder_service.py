from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from typing import TYPE_CHECKING, Any, cast
from audit_logging.services.audit_log_service import AuditLogService
from users.models.profile_reminder import (
    ProfileReminder,
    ProfileReminderStatus,
    ProfileReminderType,
)
from users.models.user import User
from users.selectors.profile_reminder_selector import (
    has_recent_sent_reminder,
)
from users.services.profile_completeness_service import (
    ProfileCompletenessService,
)

try:
    from notifications_system.services.notification_service import NotificationService
except Exception:  # pragma: no cover
    NotificationService = None  # type: ignore[assignment]
    
from users.services.profile_service import ProfileService
from core.urls.frontend_url import get_profile_url

if TYPE_CHECKING:
    from users.models.profile import UserProfile

class ProfileReminderService:
    """
    Service for profile completeness reminders.
    """

    PHONE_REMINDER_COOLDOWN_DAYS = 7
    DEFAULT_CHANNEL = "in_app"

    @classmethod
    def should_send_missing_phone_reminder(cls, user: User) -> bool:
        """
        Return True if a missing-phone reminder should be sent.
        """
        if user.website is None:
            return False

        if not user.is_active:
            return False

        if not ProfileCompletenessService.is_phone_missing(user):
            return False

        if has_recent_sent_reminder(
            user=user,
            reminder_type=ProfileReminderType.MISSING_PHONE,
            cooldown_days=cls.PHONE_REMINDER_COOLDOWN_DAYS,
        ):
            return False

        return True

    @classmethod
    @transaction.atomic
    def send_missing_phone_reminder(
        cls,
        *,
        user: User,
        channel: str | None = None,
        actor=None,
    ) -> ProfileReminder:
        """
        Send and record a missing-phone reminder.
        """
        if user.website is None:
            raise ValidationError(
                {"user": "User must belong to a website to receive reminders."}
            )

        if not ProfileCompletenessService.is_phone_missing(user):
            raise ValidationError(
                {"phone_number": "User already has a phone number."}
            )

        selected_channel = channel or cls.DEFAULT_CHANNEL

        if not cls.should_send_missing_phone_reminder(user):
            reminder = ProfileReminder.objects.create(
                user=user,
                website=user.website,
                reminder_type=ProfileReminderType.MISSING_PHONE,
                channel=selected_channel,
                status=ProfileReminderStatus.SKIPPED,
                metadata={
                    "reason": "cooldown_or_ineligible",
                },
            )
            return reminder

        try:
            cls._dispatch_missing_phone_notification(
                user=user,
                channel=selected_channel,
            )
            status = ProfileReminderStatus.SENT
            metadata: dict[str, Any] = {
                "missing_fields": ["phone_number"],
            }
        except Exception as exc:
            status = ProfileReminderStatus.FAILED
            metadata = {
                "missing_fields": ["phone_number"],
                "error": str(exc),
            }

        reminder = ProfileReminder.objects.create(
            user=user,
            website=user.website,
            reminder_type=ProfileReminderType.MISSING_PHONE,
            channel=selected_channel,
            status=status,
            metadata=metadata,
        )

        AuditLogService.log_auto(
            action="profile_missing_phone_reminder_sent",
            actor=actor,
            target=reminder,
            metadata={
                "website_id": user.website.pk,
                "subject_user_id": user.pk,
                "channel": selected_channel,
                "status": status,
            },
            changes={
                "phone_number": {
                    "from": user.phone_number or "",
                    "to": "[STILL_MISSING]",
                }
            },
        )

        return reminder
    
   
    @staticmethod
    def _dispatch_missing_phone_notification(
        *,
        user: User,
        channel: str,
    ) -> None:
        """
        Dispatch the missing-phone reminder through the centralized
        notifications system.
        """
        from notifications_system.services.notification_service import NotificationService

        NotificationService.notify(
            event_key="profile_missing_phone_reminder",
            website=user.website,
            recipient=user,
            priority="normal",
            context={
                "user_id": user.pk,
                "profile_url": get_profile_url(user),
                "website_id": user.website.pk if user.website else None,
                "missing_fields": ["phone_number"],
                "display_name": ProfileService.get_display_name(user)
                ,
            },
            channels=["email", "in_app"],
        )
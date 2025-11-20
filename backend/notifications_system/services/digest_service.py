"""Digest orchestration service."""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable, List, Optional

from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications_system.models.digest_notifications import (
    NotificationDigest,
)
from notifications_system.models.notification_group import NotificationGroup
from notifications_system.models.notification_profile import (
    GroupNotificationProfile,
)
from notifications_system.utils.email_helpers import send_website_mail
from notifications_system.utils.message_render import render_digest_email

# If your registry exposes this symbol at package root, keep this import.
# Otherwise prefer the explicit module path and alias:
# from notifications_system.registry.notification_registry import (
#     get_digest_config as _get_digest_cfg,
# )
from notifications_system.registry import get_digest_config as _get_digest_cfg

User = get_user_model()


class DigestService:
    """Service for managing user notification digests."""

    # --------- introspection / config ---------

    @staticmethod
    def is_digest(event_key: str) -> bool:
        """Return True if the event_key is configured as digestable."""
        return _get_digest_cfg(event_key) is not None

    @staticmethod
    def get_digest_config(event_key: str) -> Optional[dict]:
        """Return digest config for the given event_key, if any."""
        return _get_digest_cfg(event_key)

    @staticmethod
    def get_digest_templates(event_key: str) -> Optional[dict]:
        """Return template mapping for a digest event, or None."""
        cfg = _get_digest_cfg(event_key)
        return None if not cfg else cfg.get("templates", {})

    # --------- enqueue / scheduling ---------

    @classmethod
    def queue_digest(cls, user, event_key: str, payload: dict) -> None:
        """Enqueue a digest row for a user if enabled in config/profile.

        Args:
            user: Target user.
            event_key: Digest event key.
            payload: Context payload to merge in the digest.

        Returns:
            None. Creates a NotificationDigest row if applicable.
        """
        cfg = _get_digest_cfg(event_key)
        if not cfg or not cls.is_enabled_for_user(user, event_key):
            return

        frequency = cfg.get("frequency", "daily")
        now = timezone.now()
        scheduled_for = cls.calculate_scheduled_time(now, frequency)

        NotificationDigest.objects.create(
            user=user,
            event_key=event_key,
            payload=payload,
            scheduled_for=scheduled_for,
        )

    @staticmethod
    def calculate_scheduled_time(now, frequency: str):
        """Compute next scheduled time (8:00 local) for a given frequency.

        Args:
            now: Current timezone-aware datetime.
            frequency: "daily" or "weekly".

        Returns:
            datetime for the next digest run.
        """
        base = now.replace(hour=8, minute=0, second=0, microsecond=0)

        if frequency == "weekly":
            # Next occurrence of the same weekday at 08:00.
            days = (7 - now.weekday()) % 7
            days = 7 if days == 0 and now >= base else days
            return base + timedelta(days=days)

        # Daily: if we already passed 08:00 today, use tomorrow 08:00.
        return base if now < base else base + timedelta(days=1)

    @classmethod
    def is_enabled_for_user(cls, user, event_key: str) -> bool:
        """Return True if user has the digest enabled for the group/event.

        Looks up the NotificationGroup for event_key and the user's
        GroupNotificationProfile toggle.

        Args:
            user: Target user.
            event_key: Digest event key.

        Returns:
            bool indicating whether digests are enabled.
        """
        try:
            group = NotificationGroup.objects.get(event_key=event_key)
        except NotificationGroup.DoesNotExist:
            return False

        try:
            profile = GroupNotificationProfile.objects.get(
                user=user, group=group
            )
            return bool(profile.is_enabled)
        except GroupNotificationProfile.DoesNotExist:
            return bool(group.is_enabled_by_default)

    # --------- composition / sending ---------

    @classmethod
    def compose_digest(cls, user) -> Optional[str]:
        """Render the pending digest email HTML for a user, if due.

        Args:
            user: Target user.

        Returns:
            HTML string or None if nothing is due.
        """
        now = timezone.now()
        digests = (
            NotificationDigest.objects.filter(
                user=user, scheduled_for__lte=now, sent=False
            )
            .order_by("scheduled_for")
        )
        if not digests.exists():
            return None
        return render_digest_email(user, digests)

    @classmethod
    def send_due_digests(cls) -> None:
        """Send all due digests grouped by user."""
        now = timezone.now()
        due = (
            NotificationDigest.objects.filter(
                sent=False, scheduled_for__lte=now
            )
            .order_by("user", "scheduled_for")
        )

        grouped: dict[int, List[NotificationDigest]] = {}
        for d in due:
            grouped.setdefault(d.user_id, []).append(d)

        for user_id, items in grouped.items():
            cls.send_user_digest(user_id, items)

    @classmethod
    def send_user_digest(
        cls, user_id: int, digests: Iterable[NotificationDigest]
    ) -> None:
        """Send a single user's digest email and mark rows as sent.

        Args:
            user_id: ID of the user to notify.
            digests: Iterable of NotificationDigest rows to include.
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return

        html = render_digest_email(user, digests)
        if not html:
            return

        if user.email and cls.can_send_email(user):
            send_website_mail(
                subject="Your Activity Digest",
                message="Your activity digest is available.",
                html_message=html,
                recipient_list=[user.email],
                website=getattr(user, "website", None),
            )
            ids = [d.id for d in digests]
            NotificationDigest.objects.filter(id__in=ids).update(sent=True)

    @staticmethod
    def can_send_email(user) -> bool:
        """Return True if email delivery should be attempted for user."""
        return bool(user.email and user.is_active)

    # --------- convenience / maintenance ---------

    @classmethod
    def preview_user_digest(cls, user) -> Optional[str]:
        """Return HTML preview of the user's digest (no send)."""
        return cls.compose_digest(user)

    @classmethod
    def clear_stale_digests(cls, before_days: int = 30) -> None:
        """Delete sent digests older than a given number of days.

        Args:
            before_days: Age threshold in days for cleanup.
        """
        threshold = timezone.now() - timedelta(days=before_days)
        (
            NotificationDigest.objects.filter(
                scheduled_for__lt=threshold, sent=True
            ).delete()
        )
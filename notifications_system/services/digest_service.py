from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from notifications_system.models.digest_notifications import NotificationDigest
from notifications_system.registry import get_digest_config
from notifications_system.utils.message_render import render_digest_email
from notifications_system.utils.email_helpers import send_website_mail
from django.db.models import Q
from django.contrib.auth import get_user_model
from notifications_system.models.notification_profile import GroupNotificationProfile
from notifications_system.models.notification_group import NotificationGroup

User = get_user_model()

class DigestService:
    """Service for managing notification digests for users."""
    @staticmethod
    def is_digest(event_key: str):
        """
        Check if the event key corresponds to a digest notification.
        """
        return get_digest_config(event_key) is not None
    
    @staticmethod
    def get_digest_config(event_key: str):
        """
        Retrieves the digest configuration for the given event key.
        """
        return get_digest_config(event_key)
    
    @staticmethod
    def get_digest_templates(event_key: str):
        """
        Retrieves the templates for the digest notification based on the event key.
        """
        config = get_digest_config(event_key)
        if not config:
            return None
        return config.get('templates', {})
    
    @classmethod
    def queue_digest(cls, user, event_key, payload):
        config = get_digest_config(event_key)
        if not config or not cls.is_enabled_for_user(user, event_key):
            return

        frequency = config.get("frequency", "daily")
        now = timezone.now()
        scheduled_for = cls.calculate_scheduled_time(now, frequency)

        NotificationDigest.objects.create(
            user=user,
            event_key=event_key,
            payload=payload,
            scheduled_for=scheduled_for,
        )

    @classmethod
    def calculate_scheduled_time(cls, now, frequency):
        scheduled_for = now.replace(hour=8, minute=0, second=0, microsecond=0)

        if frequency == "weekly":
            scheduled_for += timedelta(days=(7 - now.weekday()))
        elif frequency == "daily" and now.hour >= 8:
            scheduled_for += timedelta(days=1)

        return scheduled_for

    @classmethod
    def is_enabled_for_user(cls, user, event_key):
        try:
            group = NotificationGroup.objects.get(event_key=event_key)
            profile = GroupNotificationProfile.objects.get(user=user, group=group)
            return profile.is_enabled
        except NotificationGroup.DoesNotExist:
            return False
        except GroupNotificationProfile.DoesNotExist:
            return group.is_enabled_by_default

    @classmethod
    def compose_digest(cls, user):
        now = timezone.now()
        digests = NotificationDigest.objects.filter(
            user=user,
            scheduled_for__lte=now,
            sent=False
        ).order_by("scheduled_for")

        if not digests.exists():
            return None

        return render_digest_email(user, digests)

    @classmethod
    def send_due_digests(cls):
        now = timezone.now()
        digests = (
            NotificationDigest.objects
            .filter(sent=False, scheduled_for__lte=now)
            .order_by("user", "scheduled_for")
        )

        grouped = {}
        for digest in digests:
            grouped.setdefault(digest.user_id, []).append(digest)

        for user_id, user_digests in grouped.items():
            cls.send_user_digest(user_id, user_digests)

    @classmethod
    def send_user_digest(cls, user_id, digests):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return
        user = get_user_model().objects.get(id=user_id)
        website = getattr(user, "website", None)  # or however you're tracking tenants
        rendered = render_digest_email(user, digests)

        # fallback: only send if email is valid and user has not disabled email channel
        if user.email and cls.can_send_email(user):
            send_website_mail(
                subject="Your Activity Digest",
                message="This is your digest email.",  # fallback for plaintext
                recipient_list=[user.email],
                html_message=rendered,
                website=user.website
            )
            NotificationDigest.objects.filter(id__in=[d.id for d in digests]).update(sent=True)

    @classmethod
    def can_send_email(cls, user):
        # Future-proofed: Could pull user email settings
        return user.email and user.is_active

    @classmethod
    def preview_user_digest(cls, user):
        """
        Admin/test feature: returns digest email HTML without sending.
        """
        return cls.compose_digest(user)

    @classmethod
    def clear_stale_digests(cls, before_days=30):
        """
        Clean up unneeded old digests.
        """
        threshold = timezone.now() - timedelta(days=before_days)
        NotificationDigest.objects.filter(scheduled_for__lt=threshold, sent=True).delete()

from celery import shared_task # type: ignore
from notifications_system.services.core import NotificationService
from notifications_system.enums import NotificationType
from django.utils import timezone
from notifications_system.models.digest_notifications import NotificationDigest
from notifications_system.utils.digest import summarize_entries
from users.models import User
from websites.models import Website
from notifications_system.emails.reset_notification_preferences import _send_reset_email_now
# from notifications_system.services.preferences import NotificationPreferenceResolver
from notifications_system.models.notifications import Notification
from notifications_system.template_engine import NotificationTemplateEngine
from notifications_system.services.dispatch import NotificationDispatcher 
import logging
from datetime import timedelta
from django.contrib.auth import get_user_model

# from notifications_system.models.notification_preferences import  NotificationPreference
from notifications_system.utils.summarizer import summarize_entries
from notifications_system.services.templates_registry import get_template
from core.utils.email_helpers import send_website_mail

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def send_notification_digests(frequency="daily"):
    """
    Find users with digests enabled and send them a summary.
    """
    now_time = timezone.now()

    # Set window based on frequency
    if frequency == "daily":
        since = now_time - timedelta(days=1)
    elif frequency == "weekly":
        since = now_time - timedelta(days=7)
    else:
        since = now_time - timedelta(hours=6)  # fallback

    users = User.objects.filter(notification_preferences__receive_digest=True).distinct()

    for user in users:
        pref = getattr(user, "notification_preferences", None)
        website = getattr(user, "website", None)

        if not pref or not website:
            continue

        notifications = Notification.objects.filter(
            user=user,
            created_at__gte=since,
            is_read=False,
            is_digest=False,
            website=website,
        ).order_by("-created_at")

        if not notifications.exists():
            continue  # skip user with no recent unread

        # Summarize notifications into HTML
        summary_html = summarize_entries(
            notifications,
            max=10,
            group_by_event=True,
            format="html"
        )

        subject = f"🔔 Your {frequency.capitalize()} Notification Summary"
        html_body = f"""
            <h2>Hello {user.first_name or user.username},</h2>
            <p>Here’s what you missed since {since.strftime('%b %d, %Y')}:</p>
            {summary_html}
            <p><a href="{website.domain}/dashboard/notifications">See all notifications</a></p>
        """

        # Send the digest email
        send_website_mail(
            subject=subject,
            message="",
            html_message=html_body,
            recipient_list=[user.email],
            tenant=website
        )

        # Optionally: mark them as digest-processed
        notifications.update(is_digest=True)

@shared_task(bind=True, max_retries=3)
def async_send_notification(
    self,
    user_id,
    event,
    context=None,
    website_id=None,
    actor_id=None,
    channels=None,
    category="info",
    priority=5,
    template_name=None,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False
):
    """A Celery task to send a notification to the user asynchronously."""
    try:
        from django.contrib.auth import get_user_model
        from websites.models import Website

        User = get_user_model()
        user = User.objects.get(id=user_id)
        website = Website.objects.get(id=website_id) if website_id else None
        actor = User.objects.get(id=actor_id) if actor_id else None

        return NotificationService.send(
            user=user,
            event=event,
            context=context or {},
            website=website,
            actor=actor,
            channels=channels or [NotificationType.IN_APP],
            category=category,
            priority=priority,
            template_name=template_name,
            is_critical=is_critical,
            is_digest=is_digest,
            digest_group=digest_group,
            is_silent=is_silent
        )

    except Exception as e:
        logger.error(
            f"[async_send_notification] Failed for user {user_id}: {e}",
            exc_info=True
        )
        self.retry(exc=e, countdown=60)

@shared_task
def send_daily_digests():
    """Send daily digest notifications for all users.
    This task aggregates notifications and sends them as a single digest email.
    """
    for user in User.objects.all():
        entries = NotificationDigest.objects.filter(user=user, timestamp__gte=...)
        if entries.exists():
            digest_payload = summarize_entries(entries)
            NotificationService.send(
                user=user,
                event="daily_digest",
                context={"digest": digest_payload},
                channels=[NotificationType.EMAIL],
                category="info",
                digest_group="daily_summary",
                priority=5,
                template_name=None,
                is_critical=False,
                is_digest=True,
                digest_group="daily_summary",
                is_silent=False,
                since=timezone.now() - timezone.timedelta(days=1)
            )
            entries.delete()


@shared_task
def send_digest_notifications(group_name, user_id):
    notifications = Notification.objects.filter(
        user_id=user_id, digest_group=group_name, sent=False
    )
    combined_message = "\n".join([n.message for n in notifications])
    # Replace the following with your actual email sending logic
    # For example, using Django's send_mail:
    from django.core.mail import send_mail
    user = User.objects.get(id=user_id)
    send_mail(
        subject=f"Digest Notification: {group_name}",
        message=combined_message,
        from_email=None,  # Set your default from email or use settings.DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
        fail_silently=False,
    )
    notifications.update(sent=True)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_reset_email_task(self, user_id, website_id):
    """
    Celery task to send confirmation email
    when user resets notification preferences.
    """
    try:
        user = User.objects.get(id=user_id)
        website = Website.objects.get(id=website_id)
        _send_reset_email_now(user, website)
    except (User.DoesNotExist, Website.DoesNotExist) as e:
        # Log and skip — user or website not found
        raise self.retry(exc=e)
    except Exception as e:
        # Retryable error
        raise self.retry(exc=e)
    
@shared_task
def handle_event(event_key: str, payload: dict):
    """
    Handles an event by dispatching the appropriate notification.
    """
    try:
        template_engine = NotificationTemplateEngine()
        context = build_context(event_key, payload)

        # Render the notification message
        # message = template_engine.render(event_key, context)

        # Dispatch the notification
        NotificationDispatcher.dispatch_notification(event_key, context)

    except Exception as e:
        logger.error(f"Failed to handle event {event_key}: {e}", exc_info=True)


def build_context(event_key: str, payload):
    """
    Builds the context for the notification
    based on the event key and payload.
    """
    return payload


def send_notification_task(event_key: str, context: dict):
    """
    Sends a notification by dispatching it to the appropriate channels.
    """
    NotificationDispatcher.dispatch_notification(event_key, context)
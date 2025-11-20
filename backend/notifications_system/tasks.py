# notifications_system/tasks.py
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional, Dict, Any, Iterable

from celery import shared_task  # type: ignore
from django.utils import timezone
from django.contrib.auth import get_user_model

from notifications_system.enums import NotificationType
from notifications_system.services.core import NotificationService
from notifications_system.services.dispatch import send as dispatch_send
from notifications_system.models.notifications import Notification
from notifications_system.models.digest_notifications import NotificationDigest
from notifications_system.utils.digest import summarize_entries
from notifications_system.utils.email_helpers import send_website_mail

from notifications_system.services.notification_expiry_service import NotificationExpiryService

logger = logging.getLogger(__name__)
User = get_user_model()


# ----------------------------
# Digest-related tasks
# ----------------------------

@shared_task
def send_notification_digests(frequency: str = "daily"):
    """
    Aggregate unread (non-digest) notifications since the window and email a summary.
    Users must have `notification_preferences.receive_digest=True`.
    """
    now_time = timezone.now()
    if frequency == "daily":
        since = now_time - timedelta(days=1)
    elif frequency == "weekly":
        since = now_time - timedelta(days=7)
    else:
        since = now_time - timedelta(hours=6)

    users = User.objects.filter(
        notification_preferences__receive_digest=True
    ).distinct()

    for user in users:
        website = getattr(user, "website", None)
        if not website or not getattr(user, "email", None):
            continue

        notifications = Notification.objects.filter(
            user=user,
            created_at__gte=since,
            is_digest=False,
            website=website,
        ).order_by("-created_at")

        if not notifications.exists():
            continue

        summary_html = summarize_entries(
            list(notifications),
            max=10,
            group_by_event=True,
            format="html",
        )

        subject = f"🔔 Your {frequency.capitalize()} Notification Summary"
        html_body = (
            f"<h2>Hello {user.first_name or user.username},</h2>"
            f"<p>Here’s what you missed since {since.strftime('%b %d, %Y')}:</p>"
            f"{summary_html}"
            f"<p><a href='{getattr(website, 'domain', '#')}/dashboard/notifications'>"
            f"See all notifications</a></p>"
        )

        ok = send_website_mail(
            subject=subject,
            message="",  # plain text fallback omitted
            html_message=html_body,
            recipient_list=[user.email],
            website=website,
        )

        if ok:
            # mark those items as included in a digest to avoid re-digesting
            notifications.update(is_digest=True)


@shared_task
def send_daily_digests():
    """
    If you're also storing compact NotificationDigest rows, fan them out daily.
    """
    since = timezone.now() - timedelta(days=1)
    digests = (
        NotificationDigest.objects
        .filter(created_at__gte=since, sent=False)
        .order_by("user_id", "created_at")
    )

    # Group by user
    bucket: Dict[int, list[NotificationDigest]] = {}
    for d in digests:
        bucket.setdefault(d.user_id, []).append(d)

    for user_id, items in bucket.items():
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            continue

        website = getattr(user, "website", None)
        if not website:
            continue

        # Convert digests to a compact summary
        summary_html = summarize_entries(
            items, max=20, group_by_event=True, format="html"
        )

        subject = "🔔 Your Daily Digest"
        ok = send_website_mail(
            subject=subject,
            message="",
            html_message=summary_html,
            recipient_list=[user.email],
            website=website,
        )

        if ok:
            NotificationDigest.objects.filter(
                id__in=[d.id for d in items]
            ).update(sent=True)


# ----------------------------
# Core send (async wrapper)
# ----------------------------

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def async_send_notification(
    self,
    user_id: int,
    event: str,
    payload: Optional[Dict[str, Any]] = None,
    website_id: Optional[int] = None,
    actor_id: Optional[int] = None,
    channels: Optional[Iterable[str]] = None,
    category: Optional[str] = None,
    template_name: Optional[str] = None,
    priority: int | str = 5,
    priority_label: Optional[str] = None,
    is_critical: bool = False,
    is_digest: bool = False,
    digest_group: Optional[str] = None,
    is_silent: bool = False,
    role: Optional[str] = None,
):
    """
    Send a notification asynchronously. Mirrors NotificationService.send_notification kwargs.
    """
    try:
        from websites.models import Website

        user = User.objects.get(id=user_id)
        website = Website.objects.get(id=website_id) if website_id else getattr(user, "website", None)
        actor = User.objects.get(id=actor_id) if actor_id else None

        return NotificationService.send_notification(
            user=user,
            event=event,
            payload=payload or {},
            website=website,
            actor=actor,
            channels=list(channels) if channels else [NotificationType.IN_APP],
            category=category,
            template_name=template_name,
            priority=priority,
            priority_label=priority_label,
            is_critical=is_critical,
            is_digest=is_digest,
            digest_group=digest_group,
            is_silent=is_silent,
            role=role,
        )

    except Exception as e:
        logger.error(
            f"[async_send_notification] Failed for user {user_id}: {e}",
            exc_info=True,
        )
        raise self.retry(exc=e)


# ----------------------------
# Retry hook used by core._deliver
# ----------------------------

@shared_task(bind=True, max_retries=3)
def retry_delivery(
    self,
    notification_id: int,
    channel: str,
    attempt: int,
    email_override: Optional[str] = None,
    html_message: Optional[str] = None,
):
    """
    Called by NotificationService._deliver() when async retry is needed.
    """
    try:
        n = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        logger.warning("retry_delivery: Notification %s no longer exists", notification_id)
        return False

    try:
        # Reuse the delivery path in the service
        return NotificationService._deliver(
            n,
            channel,
            html_message=html_message,
            email_override=email_override,
            attempt=attempt,
        )
    except Exception as e:
        logger.error("retry_delivery error: %s", e, exc_info=True)
        raise self.retry(exc=e, countdown=10)


# ----------------------------
# Simple event “bus” entrypoint
# ----------------------------

@shared_task
def handle_event(event_key: str, payload: dict):
    """
    Basic event handler. Expects payload to contain at least: user_id, website_id (optional).
    You can enrich/route here as needed.
    """
    user_id = payload.get("user_id")
    if not user_id:
        logger.warning("handle_event(%s): missing user_id in payload", event_key)
        return

    website_id = payload.get("website_id")
    channels = payload.get("channels")  # optional override
    role = payload.get("role")          # optional role binding

    return dispatch_send(
        user=User.objects.get(id=user_id),
        event=event_key,
        payload=payload,
        website_id=website_id,
        channels=channels,
        role=role,
    )


# ----------------------------
# Async helpers referenced by utils/
# ----------------------------

@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def async_send_website_mail(self, user_id: int, subject: str, message: str, html_message: Optional[str] = None):
    try:
        from websites.models import Website
        user = User.objects.get(id=user_id)
        website = getattr(user, "website", None)
        if not website or not user.email:
            return False
        return send_website_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            recipient_list=[user.email],
            website=website,
        )
    except Exception as e:
        logger.error("async_send_website_mail error: %s", e, exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def async_send_sms_notification(self, user_id: int, message: str):
    """
    Stub for your SMS provider. Your utils.sms_helpers calls this.
    """
    try:
        user = User.objects.get(id=user_id)
        phone = getattr(user, "phone_number", None)
        if not phone:
            return False
        # your_sms_provider.send(phone, message)
        logger.info(f"[SMS] -> {phone}: {message}")
        return True
    except Exception as e:
        logger.error("async_send_sms_notification error: %s", e, exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def async_send_push_notification(self, user_id: int, title: str, message: str):
    """
    Stub for your push provider. Your utils.push_helpers calls this.
    """
    try:
        user = User.objects.get(id=user_id)
        tokens = getattr(user, "device_tokens", []) or []
        for token in tokens:
            # push_client.send(token, title, message)
            logger.info(f"[PUSH] -> {token}: {title} | {message}")
        return True
    except Exception as e:
        logger.error("async_send_push_notification error: %s", e, exc_info=True)
        raise self.retry(exc=e)


@shared_task
def soft_expire_inapp_old(older_than_days: int = 30):
    """
    Soft-expire in-app notifications per user (marks expires_at).
    This loops users to avoid massive single-query updates across tenants.
    """
    for user in User.objects.all().only("id"):
        try:
            NotificationExpiryService.soft_expire_old_notifications(user, older_than_days=older_than_days)
        except Exception:  # keep beat resilient
            logger.exception("soft_expire_inapp_old failed for user %s", user.id)


@shared_task
def purge_expired_inapp(older_than_days: int = 90, dry_run: bool = False):
    """
    Hard-delete notifications that have been expired beyond threshold.
    """
    try:
        return NotificationExpiryService.purge_expired_notifications(older_than_days=older_than_days, dry_run=dry_run)
    except Exception:
        logger.exception("purge_expired_inapp failed")
        return 0
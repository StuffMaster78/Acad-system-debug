from __future__ import annotations

import logging
import time
from typing import Any, Dict, Iterable, Optional

from django.conf import settings
from django.utils import timezone

from notifications_system.enums import (
    NotificationPriority,
    NotificationType,
    DeliveryStatus,
)
from notifications_system.models.notifications import Notification
from notifications_system.models.notification_delivery import (
    NotificationDelivery,
)
from notifications_system.models.notification_log import NotificationLog
from notifications_system.models.broadcast_notification import (
    BroadcastNotification,
    BroadcastOverride,
)
from notifications_system.models.digest_notifications import (
    NotificationDigest,
)
from notifications_system.registry.template_registry import (
    get_template,
    get_template_name,  # kept for hybrid file skins
)
from notifications_system.registry.role_bindings import (
    get_channels_for_role,
)
from notifications_system.registry.forced_channels import (
    ForcedChannelRegistry,
)
from notifications_system.services.preferences import (
    NotificationPreferenceResolver,
)
from notifications_system.utils.dnd import is_dnd_now
from notifications_system.utils.priority_mapper import (
    get_priority_from_label,
)
from notifications_system.utils.filter_preferred_channels import (
    filter_channels_by_user_preferences,
)
from notifications_system.utils.fallbacks import FallbackOrchestrator
from notifications_system.utils.dedupe import allow_once

logger = logging.getLogger(__name__)


class NotificationService:
    """Central orchestrator for notifications.

    Responsibilities:
      * Validate inputs (user, event, website).
      * Respect mute, DND, preferences, and forced channels.
      * Render class templates (source of truth).
      * Create the Notification row.
      * Deliver via channel backends.
      * Record deliveries and logs centrally.
      * Coordinate retries/backoff and fallbacks.
      * Publish SSE/polling broadcasts.
      * Support digests and broadcast events.

    All sends must flow through this service.
    """

    @staticmethod
    def send_notification(
        *,
        user,
        event: str,
        payload: Optional[Dict[str, Any]] = None,
        website=None,
        actor=None,
        channels: Optional[Iterable[str]] = None,
        category: Optional[str] = None,
        template_name: Optional[str] = None,
        priority: int | str = 5,
        priority_label: Optional[str] = None,
        is_critical: bool = False,
        is_digest: bool = False,
        digest_group: Optional[str] = None,
        is_silent: bool = False,
        email_override: Optional[str] = None,
        global_broadcast: bool = False,
        groups: Optional[Iterable[str]] = None,
        role: Optional[str] = None,
    ):
        """Send a notification and fan out to delivery backends.

        Args:
            user: Target user (must be authenticated).
            event: Canonical event key (e.g., "order.created").
            payload: Event context sent to templates/backends.
            website: Tenant/site object (required).
            actor: Optional actor who triggered the event.
            channels: Optional explicit channels to send on.
            category: Arbitrary string category.
            template_name: Optional render skin hint.
            priority: Integer or label for priority.
            priority_label: Legacy label (compat).
            is_critical: If True, may bypass mute.
            is_digest: If True, mark for digest grouping.
            digest_group: Explicit digest key.
            is_silent: If True, persist but do not deliver.
            email_override: Override recipient email.
            global_broadcast: Publish to global stream.
            groups: Optional SSE/polling groups.
            role: Optional role for role-channel mapping.

        Returns:
            Notification ORM instance, broadcast object, or None.
        """
        # ----- Basic validation
        if not user or not getattr(user, "is_authenticated", False):
            logger.warning(
                "Notification skipped: unauthenticated/invalid user."
            )
            return None
        if not event:
            logger.warning("Notification skipped: empty event key.")
            return None
        if not website:
            logger.warning("Notification skipped: no website provided.")
            return None

        payload = dict(payload or {})
        payload.setdefault("user_id", user.id)
        payload.setdefault("website_id", getattr(website, "id", None))

        # ----- Deduplication (once-only)
        dedupe_secs = getattr(settings, "NOTIFICATION_DEDUPE_WINDOW_SECONDS", 45)
        if dedupe_secs:
            allowed = allow_once(
                user.id, event,
                getattr(website, "id", None),
                payload=payload,
                ttl=dedupe_secs
            )
            if not allowed:
                logger.info(
                    "Deduped notification for user=%s event=%s",
                    user.id, event
                )
                return None
        # ----- Profiles & preferences
        if not hasattr(user, "notification_profile"):
            logger.warning(
                "User %s has no notification_profile. Consider defaults.",
                user,
            )

        if not hasattr(user, "notification_preferences"):
            logger.info(
                "User %s has no notification_preferences. Assigning "
                "defaults.",
                user,
            )
            NotificationPreferenceResolver.assign_default_preferences(user)

        # Respect mute unless critical
        is_muted = getattr(getattr(user, "pref", None), "is_muted", lambda:
                           False)()
        if is_muted and not is_critical:
            logger.info(
                "User %s is muted. Skipping non-critical notification.",
                user,
            )
            return None

        # ----- DND filter
        profile = getattr(user, "notification_profile", None)
        if is_dnd_now(profile):
            dnd_channels = getattr(profile, "dnd_channels", []) or []
            channels = [c for c in (channels or []) if c not in dnd_channels]
            if not channels:
                logger.info(
                    "User %s is in DND; no eligible channels remain.",
                    user,
                )
                return None

        # ----- Resolve channels (forced > explicit > role > prefs)
        forced = ForcedChannelRegistry.get(event, set())
        if forced:
            resolved_channels = list(forced)
        elif channels:
            resolved_channels = list(channels)
        else:
            user_role = role or getattr(user, "role", None)
            role_channels = (
                get_channels_for_role(event, user_role) if user_role else []
            )
            if role_channels:
                resolved_channels = list(role_channels)
            else:
                resolved_channels = (
                    NotificationPreferenceResolver.get_effective_preferences(
                        user=user,
                        website=website,
                    )
                )

        # Filter by user prefs (only when not forced)
        if not forced:
            resolved_channels = filter_channels_by_user_preferences(
                user=user,
                channels=resolved_channels,
                website=website,
            )

        if not resolved_channels:
            # As last resort, in_app
            resolved_channels = [NotificationType.IN_APP]

        # ----- Priority normalize
        if isinstance(priority, str):
            pr = get_priority_from_label(priority)
            priority = pr or NotificationPriority.NORMAL
        if priority is None:
            priority = NotificationPriority.NORMAL
        if priority_label and isinstance(priority_label, str):
            pr = get_priority_from_label(priority_label)
            priority = pr or priority

        # ----- Broadcasts
        broadcast = BroadcastNotification.objects.filter(
            event_type=event,
            is_active=True,
        ).first()
        if broadcast:
            targeted = NotificationPreferenceResolver.get_target_users(
                broadcast
            )
            for target in targeted:
                NotificationService.send_notification(
                    user=target,
                    event=event,
                    payload=payload,
                    website=website,
                    actor=actor,
                    channels=resolved_channels,
                    category=category,
                    template_name=template_name,
                    priority=priority,
                    is_critical=is_critical,
                    is_digest=is_digest,
                    digest_group=digest_group,
                    is_silent=is_silent,
                    email_override=email_override,
                    global_broadcast=global_broadcast,
                    groups=groups,
                )
            return broadcast

        # ----- Broadcast override
        override = BroadcastOverride.objects.filter(
            event_type=event,
            active=True,
        ).first()
        if override:
            if override.title:
                payload["title"] = override.title
            if override.message:
                payload["message"] = override.message
            if override.force_channels:
                resolved_channels = list(override.force_channels)

        # ----- Digest marking
        if is_digest and profile:
            digest_group = digest_group or f"{event}_{user.id}"
            payload["digest_group"] = digest_group
            payload["is_digest"] = True

        # ----- Render (class-based template)
        tmpl = get_template(event)
        if not tmpl:
            logger.warning(
                "No class-based template registered for event '%s'", event
            )
            return None

        try:
            title, text_message, html_message = tmpl.render(payload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Template render failed for '%s': %s", event, exc)
            return None

        # ----- Create DB Notification
        primary_channel = resolved_channels[0]
        notification = Notification.objects.create(
            user=user,
            actor=actor,
            event=event,
            payload=payload,
            website=website,
            type=primary_channel,
            title=title,
            message=text_message,
            rendered_title=title,
            rendered_message=text_message,
            rendered_link=payload.get("link"),
            rendered_payload=payload,
            template_name=template_name or getattr(tmpl, "event_name",
                                                   "generic"),
            template_version=payload.get("version"),
            category=category or "info",
            priority=priority,
            is_critical=is_critical,
            is_digest=is_digest,
            digest_group=digest_group,
            is_silent=is_silent,
            status=DeliveryStatus.PENDING,
        )

        if is_silent:
            return notification

        # ----- Deliver per channel
        sent_any = False
        for channel in resolved_channels:
            # Allow prefs to veto unless forced
            if not forced and not NotificationService._is_channel_enabled(
                user,
                getattr(user, "notification_preferences", None),
                channel,
            ):
                continue

            ok = False
            try:
                ok = NotificationService._deliver(
                    notification,
                    channel,
                    html_message=html_message,
                    email_override=email_override,
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "[%s] delivery crashed for user %s: %s",
                    channel,
                    user,
                    exc,
                )
                NotificationDelivery.objects.create(
                    notification=notification,
                    channel=channel,
                    status=DeliveryStatus.FAILED,
                    error_message=str(exc),
                    attempts=1,
                )
                NotificationLog.objects.create(
                    notification=notification,
                    channel=channel,
                    success=False,
                    response_code=500,
                    status=DeliveryStatus.FAILED,
                    message=f"[{channel.upper()}] Exception on send",
                    timestamp=timezone.now(),
                )
                ok = False

            ok = False if ok is None else bool(ok)
            sent_any = sent_any or ok

        # ----- Log summary
        NotificationLog.objects.create(
            notification=notification,
            channel=primary_channel,
            success=sent_any,
            response_code=200 if sent_any else 500,
            status=DeliveryStatus.SENT if sent_any else DeliveryStatus.FAILED,
            message="Sent via: " + ", ".join(resolved_channels),
            timestamp=timezone.now(),
        )

        # ----- Publish to broadcaster (SSE/polling)
        try:
            from notifications_system.events import NotificationBroadcaster
            NotificationBroadcaster.publish(
                payload,
                user_id=user.id if user else None,
                group=groups,
                global_broadcast=global_broadcast,
                notification_id=notification.id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Broadcast publish failed for notification %s: %s",
                notification.id,
                exc,
            )

        notification.status = DeliveryStatus.SENT
        notification.sent_at = timezone.now()
        notification.save(update_fields=["status", "sent_at"])
        return notification

    # -----------------------
    # Helpers / fan-out core
    # -----------------------

    @staticmethod
    def _is_channel_enabled(user, preferences, channel: str) -> bool:
        """Return whether a channel is enabled by user preferences."""
        if not preferences:
            return True
        if channel == NotificationType.EMAIL:
            return getattr(preferences, "receive_email", True)
        if channel == NotificationType.SMS:
            return getattr(preferences, "receive_sms", True)
        if channel == NotificationType.PUSH:
            return getattr(preferences, "receive_push", True)
        if channel == NotificationType.IN_APP:
            return getattr(preferences, "receive_in_app", True)
        if channel == NotificationType.WEBHOOK:
            return getattr(preferences, "receive_webhook", True)
        if channel == NotificationType.SSE:
            return getattr(preferences, "receive_sse", True)
        if channel == NotificationType.WS:
            return getattr(preferences, "receive_ws", True)
        return True

    @staticmethod
    def _deliver(
        notification,
        channel: str,
        *,
        html_message: Optional[str] = None,
        email_override: Optional[str] = None,
        attempt: int = 1,
    ) -> bool:
        """Deliver a single channel and record results.

        Unwraps DeliveryResult from the backend, records delivery and log
        rows, and orchestrates retries/backoff.

        Args:
            notification: Notification ORM instance.
            channel: Channel key (e.g., "email").
            html_message: Optional pre-rendered HTML for backends.
            email_override: Optional recipient override for email.
            attempt: Attempt number (1-based).

        Returns:
            True on success, False otherwise.
        """
        try:
            # Lazy import avoids cycles with delivery map.
            from notifications_system.delivery import CHANNEL_BACKENDS
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                f"Delivery registry import failed: {exc}"
            ) from exc

        backend_cls = CHANNEL_BACKENDS.get(channel)
        if not backend_cls:
            raise ValueError(f"Unsupported delivery channel: {channel}")

        backend = backend_cls(
            notification,
            channel_config={
                "html_message": html_message,
                "email_override": email_override,
                # Backends may call get_template_name(...) if needed.
            },
        )

        success = False
        message = "delivery not attempted"
        meta = None

        try:
            result = backend.send()
            if hasattr(result, "success"):
                success = bool(result.success)
                message = getattr(result, "message", "") or ""
                meta = getattr(result, "meta", None)
            else:
                # Legacy backends may return bare bools.
                success = bool(result)
                message = "legacy backend bool result"
                meta = None
        except Exception as exc:  # noqa: BLE001
            logger.exception("[%s] Error during delivery: %s", channel, exc)
            success = False
            message = f"exception: {exc}"
            meta = None

        NotificationDelivery.objects.create(
            notification=notification,
            channel=channel,
            status=DeliveryStatus.SENT if success else DeliveryStatus.FAILED,
            sent_at=timezone.now(),
            attempts=attempt,
        )

        try:
            NotificationLog.objects.create(
                notification=notification,
                channel=channel,
                success=success,
                response_code=200 if success else 500,
                status=DeliveryStatus.SENT if success else DeliveryStatus.FAILED,
                message=f"[{channel}] attempt {attempt}: "
                        f"{message}".strip(),
                timestamp=timezone.now(),
                # If your model supports JSON meta, add it here.
            )
        except Exception:  # noqa: BLE001
            logger.debug("NotificationLog write skipped/failed.", exc_info=True)

        max_retries = getattr(settings, "DEFAULT_MAX_RETRIES", 3)
        use_sync = getattr(settings, "USE_SYNC_RETRIES", False)
        backoff = getattr(settings, "CHANNEL_BACKOFFS", {}).get(channel, 10)

        if not success and attempt < max_retries:
            if use_sync:
                time.sleep(backoff)
                return NotificationService._deliver(
                    notification,
                    channel,
                    html_message=html_message,
                    email_override=email_override,
                    attempt=attempt + 1,
                )
            try:
                # Optional Celery task (configure if you have one).
                from notifications_system.tasks import retry_delivery
                retry_delivery.apply_async(
                    kwargs={
                        "notification_id": notification.id,
                        "channel": channel,
                        "attempt": attempt + 1,
                        "email_override": email_override,
                        "html_message": html_message,
                    },
                    countdown=backoff,
                )
            except Exception:  # noqa: BLE001
                time.sleep(backoff)
                return NotificationService._deliver(
                    notification,
                    channel,
                    html_message=html_message,
                    email_override=email_override,
                    attempt=attempt + 1,
                )

        if not success:
            FallbackOrchestrator.handle_fallbacks(
                notification,
                channel,
                html_message=html_message,
                email_override=email_override,
            )

        return success

    # -----------------------
    # Optional extras kept
    # -----------------------

    @staticmethod
    def send_broadcast(
        event: str,
        title: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        website=None,
        channels: Optional[Iterable[str]] = None,
        priority: int = NotificationPriority.NORMAL,
    ):
        """Create a broadcast and fan out to targeted users."""
        channels = list(
            channels or [NotificationType.IN_APP, NotificationType.EMAIL]
        )
        broadcast = BroadcastNotification.objects.create(
            event_type=event,
            title=title,
            message=message,
            context=context or {},
            website=website,
            priority=priority,
        )
        targeted = NotificationPreferenceResolver.get_target_users(
            broadcast
        )
        for target in targeted:
            NotificationService.send_notification(
                user=target,
                event=event,
                payload=context or {},
                website=website,
                channels=channels,
                is_critical=False,
            )
        return broadcast

    @staticmethod
    def send_digests(group: str, since=None):
        """Send digest emails for a group since a given time."""
        since = since or timezone.now() - timezone.timedelta(days=1)
        digests = NotificationDigest.objects.filter(
            group=group,
            created_at__gte=since,
        )
        for digest in digests:
            for user in digest.users.all():
                NotificationService.send_notification(
                    user=user,
                    event=digest.event,
                    payload=digest.context,
                    website=digest.website,
                    channels=[NotificationType.EMAIL],
                    is_digest=True,
                )
        return digests
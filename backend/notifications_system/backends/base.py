# notifications_system/backends/base.py
"""
Base classes for all delivery backends.

Every channel backend (email, in-app, Telegram, WhatsApp, SSE,
WebSocket, push) inherits from BaseDeliveryBackend and implements
one method: send() → DeliveryResult.

The pipeline (send_channel_notification task) calls backend.send()
and records the result on the Delivery model. It does not care
what happens inside send() — only whether it succeeded or failed
and what the provider said.

DeliveryResult is a frozen dataclass — immutable once created.
Backends return it, they never mutate it.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# DeliveryResult
# ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DeliveryResult:
    """
    Immutable result returned by every backend's send() method.

    The pipeline reads this to decide:
        success=True  → mark Delivery SENT, update Notification status
        success=False → record error, schedule retry or attempt fallback

    Fields:
        success:        True if the provider accepted the message.
                        False on any failure — validation, network,
                        provider error, or missing config.

        message:        Human-readable outcome description.
                        On success: brief confirmation e.g. 'Email sent.'
                        On failure: what went wrong e.g. 'SMTP timeout.'

        provider_msg_id: Provider's message ID for tracking and
                        debugging. e.g. SendGrid's X-Message-Id,
                        Telegram's message_id, Mailgun's id field.
                        Empty string if not applicable or unavailable.

        error_code:     Short machine-readable error code.
                        Used by the pipeline to decide retry strategy
                        and by support to diagnose delivery failures.
                        Empty string on success.

                        Standard codes:
                            NO_EMAIL            recipient has no email address
                            NO_BODY             template rendered no body
                            NO_BACKEND          no backend for this channel
                            NO_CONFIG           provider not configured
                            NO_CHAT_ID          user has no Telegram chat ID
                            NO_PHONE            user has no phone number
                            NO_FCM_TOKEN        user has no FCM token
                            BACKEND_CRASH       backend raised an exception
                            SEND_ERROR          provider API or SMTP error
                            INVALID_CHANNEL     channel type is wrong
                            META_UPDATE_FAILED  unread count update failed

        meta:           Optional dict for any extra provider data
                        worth recording — rate limit headers,
                        bounce codes, provider status codes etc.
                        Not used by the pipeline — for debugging only.
    """
    success: bool
    message: str = ''
    provider_msg_id: str = ''
    error_code: str = ''
    meta: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self):
        # Enforce types — frozen=True prevents assignment after init
        # but does not enforce types so we validate here
        if not isinstance(self.success, bool):
            raise TypeError(
                f"DeliveryResult.success must be bool, "
                f"got {type(self.success).__name__}"
            )
        if not isinstance(self.message, str):
            object.__setattr__(self, 'message', str(self.message))
        if not isinstance(self.provider_msg_id, str):
            object.__setattr__(self, 'provider_msg_id', str(self.provider_msg_id))
        if not isinstance(self.error_code, str):
            object.__setattr__(self, 'error_code', str(self.error_code))

    @property
    def is_retryable(self) -> bool:
        """
        True if this failure is worth retrying.

        Configuration errors (NO_CONFIG, NO_EMAIL, NO_CHAT_ID etc)
        will not resolve on retry — no point retrying them.

        Network and provider errors (SEND_ERROR, BACKEND_CRASH)
        may resolve on retry — worth attempting.
        """
        non_retryable = {
            'NO_EMAIL',
            'NO_BODY',
            'NO_BACKEND',
            'NO_CONFIG',
            'NO_CHAT_ID',
            'NO_PHONE',
            'NO_FCM_TOKEN',
            'INVALID_CHANNEL',
            'INVALID_CHANNEL_TYPE',
        }
        return self.error_code not in non_retryable

    def __str__(self) -> str:
        if self.success:
            return (
                f"DeliveryResult(success=True"
                f"{f', msg_id={self.provider_msg_id}' if self.provider_msg_id else ''})"
            )
        return (
            f"DeliveryResult(success=False"
            f", error_code={self.error_code}"
            f", message={self.message!r})"
        )


# ─────────────────────────────────────────────────────────────────
# BaseDeliveryBackend
# ─────────────────────────────────────────────────────────────────

class BaseDeliveryBackend(ABC):
    """
    Abstract base class for all delivery backends.

    Every channel — email, in-app, Telegram, WhatsApp, SSE,
    WebSocket, push — is a subclass that implements send().

    The pipeline (send_channel_notification task) works with
    this interface only. It never knows which concrete backend
    it is calling. Adding a new channel means adding a new
    subclass — nothing in the pipeline changes.

    Subclass contract:
        - Set channel = 'your_channel_name' as a class attribute
        - Implement send() → DeliveryResult
        - Never raise from send() — catch all exceptions and
          return DeliveryResult(success=False, ...)
        - Never mutate self.delivery — it is read-only context

    Available on every instance via self:
        self.delivery       the Delivery model instance
        self.user           delivery.user (recipient)
        self.website        delivery.website (tenant)
        self.notification   delivery.notification
        self.rendered       delivery.rendered (pre-rendered content dict)
        self.payload        delivery.payload (original event payload)
        self.channel        delivery.channel (string)
        self.priority       delivery.priority

    Usage:
        backend = EmailBackend(delivery)
        result = backend.send()
        # result is a DeliveryResult
    """

    #: Channel identifier — must match NotificationChannel enum value
    #: Set on every subclass e.g. channel = 'email'
    channel: str = 'unknown'

    def __init__(self, delivery) -> None:
        """
        Initialise with a Delivery model instance.

        Args:
            delivery: Delivery model instance for this send attempt.
                      Must have user, website, notification,
                      rendered, payload, channel, priority populated.
        """
        if delivery is None:
            raise ValueError(
                f"{self.__class__.__name__}: delivery cannot be None."
            )
        self._delivery = delivery

    # ─────────────────────────────────────────────────
    # Convenience properties — read-only access to
    # the delivery and its related objects
    # ─────────────────────────────────────────────────

    @property
    def delivery(self):
        """The Delivery model instance."""
        return self._delivery

    @property
    def user(self):
        """Recipient user instance."""
        return self._delivery.user

    @property
    def website(self):
        """Website (tenant) instance."""
        return self._delivery.website

    @property
    def notification(self):
        """Parent Notification instance."""
        return self._delivery.notification

    @property
    def rendered(self) -> Dict[str, Any]:
        """
        Pre-rendered content dict from TemplateService.

        Email keys:    subject, body_html, body_text
        In-app keys:   title, message
        All channels:  event_key, category, priority

        Always returns a dict — never None.
        """
        return self._delivery.rendered or {}

    @property
    def payload(self) -> Dict[str, Any]:
        """
        Original event payload stored on the Delivery row.
        Contains context, channels, flags from the outbox.
        Always returns a dict — never None.
        """
        return self._delivery.payload or {}

    @property
    def priority(self) -> str:
        """Delivery priority string."""
        return self._delivery.priority

    # ─────────────────────────────────────────────────
    # Abstract interface
    # ─────────────────────────────────────────────────

    @abstractmethod
    def send(self) -> DeliveryResult:
        """
        Attempt to deliver this notification.

        Must be implemented by every subclass.

        Contract:
            - Always returns a DeliveryResult — never raises
            - Returns DeliveryResult(success=True) on success
            - Returns DeliveryResult(success=False, error_code=...) on failure
            - Never mutates self.delivery
            - Never calls self.delivery.record_attempt() —
              the pipeline does that after send() returns
            - Catches all exceptions internally and converts
              them to DeliveryResult(success=False)

        Returns:
            DeliveryResult indicating success or failure.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement send()."
        )

    # ─────────────────────────────────────────────────
    # Shared helpers available to all subclasses
    # ─────────────────────────────────────────────────

    def _get_recipient_email(self) -> Optional[str]:
        """
        Return the recipient's email address.
        Returns None if the user has no email or it is blank.
        """
        email = getattr(self.user, 'email', None)
        if not email or not email.strip():
            return None
        return email.strip()

    def _get_recipient_phone(self) -> Optional[str]:
        """
        Return the recipient's phone number in E.164 format.
        Returns None if the user has no phone number.
        """
        phone = getattr(self.user, 'phone_number', None)
        if not phone or not phone.strip():
            return None
        return phone.strip()

    def _get_website_settings(self):
        """
        Return GlobalNotificationSystemSettings for this website.
        Returns None if not configured.
        """
        try:
            from notifications_system.models.notification_settings import (
                GlobalNotificationSystemSettings,
            )
            return GlobalNotificationSystemSettings.for_website(self.website)
        except Exception as exc:
            logger.warning(
                "%s._get_website_settings(): failed for website=%s: %s",
                self.__class__.__name__,
                getattr(self.website, 'id', None),
                exc,
            )
            return None

    def _log_attempt(self, result: DeliveryResult) -> None:
        """
        Log the delivery attempt outcome at the appropriate level.
        Called internally by subclasses that want consistent logging.
        Most subclasses let the pipeline log for them — this is
        available for backends that need more granular logging.
        """
        if result.success:
            logger.info(
                "%s: delivery=%s channel=%s succeeded "
                "provider_msg_id=%s.",
                self.__class__.__name__,
                self._delivery.id,
                self.channel,
                result.provider_msg_id,
            )
        else:
            logger.warning(
                "%s: delivery=%s channel=%s failed "
                "error_code=%s message=%s.",
                self.__class__.__name__,
                self._delivery.id,
                self.channel,
                result.error_code,
                result.message,
            )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"delivery={getattr(self._delivery, 'id', None)}, "
            f"channel={self.channel!r}, "
            f"user={getattr(self.user, 'id', None)})"
        )
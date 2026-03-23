# notifications_system/backends/providers/base.py
"""
Base class for email provider backends.

Email delivery has its own provider abstraction layer beneath
the main backend abstraction:

    EmailBackend (backends/email.py)
        └── calls EmailService.get_backend(website)
                └── returns a BaseEmailBackend subclass
                        └── SendGridBackend
                        └── MailgunBackend
                        └── SESBackend
                        └── GmailBackend
                        └── ConsoleEmailBackend

This separation exists because email has multiple competing
providers with different APIs, authentication schemes, and
response formats. Each provider is a clean swap — same
interface, different implementation.

BaseEmailBackend is different from BaseDeliveryBackend:

    BaseDeliveryBackend   channel-level abstraction
                          receives a Delivery instance
                          knows about users, websites, rendered content
                          used by the pipeline task

    BaseEmailBackend      provider-level abstraction
                          receives pre-rendered strings only
                          knows nothing about users, websites, or models
                          used by EmailBackend and EmailService
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# EmailSendResult
# ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EmailSendResult:
    """
    Immutable result returned by every provider's send() method.

    Different from DeliveryResult — this is provider-specific.
    EmailBackend converts this into a DeliveryResult after send()
    returns.

    Fields:
        success:        True if the provider accepted the message
                        for delivery. Does not mean the email was
                        received — only that the provider queued it.

        message_id:     Provider's message ID for tracking.
                        e.g. SendGrid X-Message-Id,
                             Mailgun id field,
                             SES MessageId.
                        Empty string if unavailable.

        error_code:     Short machine-readable error code.
                        Empty string on success.

                        Provider error codes:
                            AUTH_ERROR          invalid API key
                            RATE_LIMITED        provider rate limit hit
                            INVALID_RECIPIENT   provider rejected recipient
                            SEND_FAILED         provider returned error
                            TIMEOUT             request timed out
                            CONNECTION_ERROR    could not reach provider

        error_message:  Human-readable error description.
                        Empty string on success.

        status_code:    HTTP status code from provider API.
                        0 if not applicable (e.g. SMTP).

        meta:           Optional extra provider response data.
                        Not used by the pipeline — for debugging.
    """
    success: bool
    message_id: str = ''
    error_code: str = ''
    error_message: str = ''
    status_code: int = 0
    meta: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self):
        if not isinstance(self.success, bool):
            raise TypeError(
                f"EmailSendResult.success must be bool, "
                f"got {type(self.success).__name__}"
            )

    @property
    def is_retryable(self) -> bool:
        """
        True if this failure is worth retrying.

        Rate limits and timeouts resolve on retry.
        Auth errors and invalid recipients do not.
        """
        non_retryable = {
            'AUTH_ERROR',
            'INVALID_RECIPIENT',
        }
        return self.error_code not in non_retryable

    def __str__(self) -> str:
        if self.success:
            return (
                f"EmailSendResult(success=True"
                f"{f', message_id={self.message_id}' if self.message_id else ''})"
            )
        return (
            f"EmailSendResult(success=False"
            f", error_code={self.error_code}"
            f", error_message={self.error_message!r}"
            f"{f', status_code={self.status_code}' if self.status_code else ''})"
        )


# ─────────────────────────────────────────────────────────────────
# EmailMessage
# ─────────────────────────────────────────────────────────────────

@dataclass
class EmailMessage:
    """
    A fully assembled email ready for sending.

    Built by EmailBackend from the Delivery's rendered content
    and GlobalNotificationSystemSettings. Passed to the provider's
    send() method.

    This dataclass is the clean interface boundary between
    EmailBackend (which knows about models and settings) and
    BaseEmailBackend subclasses (which know only about sending).

    Fields:
        to:             Recipient email address
        subject:        Email subject line
        body_html:      HTML body — primary content
        body_text:      Plain text fallback
        from_name:      Sender display name e.g. 'Writing Platform'
        from_address:   Sender email address e.g. 'noreply@example.com'
        reply_to:       Optional reply-to address
        cc:             Optional CC addresses
        bcc:            Optional BCC addresses
        headers:        Optional custom email headers
        attachments:    Optional attachments — list of dicts with
                        filename, content (bytes), content_type
        tags:           Optional provider tags for tracking
                        e.g. ['order-completed', 'transactional']
        metadata:       Optional provider metadata dict
    """
    to: str
    subject: str
    body_html: str
    body_text: str
    from_name: str
    from_address: str
    reply_to: Optional[str] = None
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.to or not self.to.strip():
            raise ValueError("EmailMessage.to cannot be empty.")
        if not self.subject and not self.body_html and not self.body_text:
            raise ValueError(
                "EmailMessage must have at least a subject or body."
            )

    @property
    def from_header(self) -> str:
        """
        Formatted From header.
        e.g. 'Writing Platform <noreply@example.com>'
        or just 'noreply@example.com' if no from_name.
        """
        if self.from_name and self.from_address:
            return f"{self.from_name} <{self.from_address}>"
        return self.from_address or self.from_name

    def has_html(self) -> bool:
        return bool(self.body_html and self.body_html.strip())

    def has_text(self) -> bool:
        return bool(self.body_text and self.body_text.strip())

    def has_attachments(self) -> bool:
        return bool(self.attachments)

    def __repr__(self) -> str:
        return (
            f"EmailMessage("
            f"to={self.to!r}, "
            f"subject={self.subject!r}, "
            f"from={self.from_header!r})"
        )


# ─────────────────────────────────────────────────────────────────
# BaseEmailBackend
# ─────────────────────────────────────────────────────────────────

class BaseEmailBackend(ABC):
    """
    Abstract base class for email provider backends.

    Each provider (SendGrid, Mailgun, SES, Gmail, Console)
    subclasses this and implements send().

    Subclass contract:
        - Set provider_name as a class attribute
        - Implement send(message) → EmailSendResult
        - Never raise from send() — catch all exceptions and
          return EmailSendResult(success=False, ...)
        - Never modify the EmailMessage passed to send()
        - self.config contains provider credentials and settings
          passed from GlobalNotificationSystemSettings or
          Django settings

    Usage:
        # EmailService resolves the right backend
        backend = EmailService.get_backend(website)

        # EmailBackend builds the message and calls send()
        result = backend.send(message)

        # result is an EmailSendResult
        if result.success:
            delivery_result = DeliveryResult(
                success=True,
                provider_msg_id=result.message_id,
            )
    """

    #: Human-readable provider name for logging
    #: e.g. 'SendGrid', 'Mailgun', 'AWS SES', 'Gmail', 'Console'
    provider_name: str = 'Unknown'

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialise with provider configuration.

        Args:
            config: Dict of provider credentials and settings.
                    Contents depend on the provider:

                    SendGrid:   {'api_key': 'SG.xxx'}
                    Mailgun:    {'api_key': 'key-xxx', 'domain': 'mg.example.com'}
                    SES:        {'aws_access_key_id': '...', 'aws_secret_access_key': '...', 'region_name': '...'}
                    Gmail:      {'email': 'you@gmail.com', 'password': 'app-password'}
                    Console:    {}
        """
        if not isinstance(config, dict):
            raise TypeError(
                f"{self.__class__.__name__}: config must be a dict, "
                f"got {type(config).__name__}"
            )
        self.config = config
        self._validate_config()

    @abstractmethod
    def send(self, message: EmailMessage) -> EmailSendResult:
        """
        Send an email via this provider.

        Must be implemented by every subclass.

        Contract:
            - Accepts an EmailMessage instance
            - Always returns an EmailSendResult — never raises
            - Never modifies the EmailMessage
            - On success: returns EmailSendResult(success=True, message_id=...)
            - On failure: returns EmailSendResult(success=False, error_code=...)
            - Catches all exceptions and converts to EmailSendResult

        Args:
            message: Fully assembled EmailMessage ready to send.

        Returns:
            EmailSendResult indicating success or failure.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement send()."
        )

    def _validate_config(self) -> None:
        """
        Validate provider configuration on initialisation.

        Override in subclasses to check required config keys.
        Raise RuntimeError with a clear message if config is invalid.

        Called automatically from __init__ — do not call manually.

        Example:
            def _validate_config(self) -> None:
                if not self.config.get('api_key'):
                    raise RuntimeError(
                        "SendGridBackend requires 'api_key' in config."
                    )
        """
        pass  # Base implementation is a no-op — subclasses override

    def health_check(self) -> bool:
        """
        Verify this provider is reachable and configured correctly.

        Override in subclasses to implement a real connectivity check.
        Used by the health check endpoint and validate_templates command.

        Returns:
            True if the provider is reachable and the credentials work.
            False if not. Never raises.
        """
        return True  # Default — assume healthy unless overridden

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Return non-sensitive provider information for logging
        and admin display.

        Never returns credentials — only provider name, region,
        domain, or other non-sensitive metadata.

        Override in subclasses to return meaningful info.
        """
        return {'provider': self.provider_name}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider_name!r})"
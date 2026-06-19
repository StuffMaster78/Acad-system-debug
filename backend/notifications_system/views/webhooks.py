"""
Webhook endpoints for email provider feedback.

Each provider posts events here when emails bounce, generate
spam complaints, or are unsubscribed. We write the raw event
to ProviderWebhookEvent immediately (never lose the event),
then process it to update EmailSuppression.

Routes (add to urls.py):
    path('webhooks/sendgrid/', SendgridWebhookView.as_view()),
    path('webhooks/ses/', SESWebhookView.as_view()),
    path('webhooks/mailgun/', MailgunWebhookView.as_view()),

Security:
    Each view validates a provider-specific signature or token.
    Requests failing validation are rejected with 403.
    Set the corresponding secret in Django settings:
        SENDGRID_WEBHOOK_VERIFICATION_KEY
        MAILGUN_WEBHOOK_SIGNING_KEY
    SES uses SNS topic subscription confirmation + message signing.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import re
import time
import urllib.request

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from notifications_system.models.email_suppression import (
    EmailSuppression,
    ProviderWebhookEvent,
    SuppressionReason,
)

logger = logging.getLogger(__name__)

# ── Security helpers ───────────────────────────────────────────────────────────

_AWS_SNS_URL_RE = re.compile(r'^https://sns\.[a-z0-9-]+\.amazonaws\.com/')

# SNS field ordering per AWS signature specification
_SNS_SIGN_FIELDS: dict[str, list[str]] = {
    'Notification': ['Message', 'MessageId', 'Subject', 'Timestamp', 'TopicArn', 'Type'],
    'SubscriptionConfirmation': ['Message', 'MessageId', 'SubscribeURL', 'Timestamp', 'Token', 'TopicArn', 'Type'],
    'UnsubscribeConfirmation': ['Message', 'MessageId', 'SubscribeURL', 'Timestamp', 'Token', 'TopicArn', 'Type'],
}


def _verify_sendgrid_ecdsa(public_key_pem: str, body: bytes, signature: str, timestamp: str) -> bool:
    """
    Verify a SendGrid Event Webhook ECDSA-SHA256 signature.

    SendGrid signs: timestamp_value + raw_body (bytes, then encoded as UTF-8).
    The public key is the ECDSA P-256 key from the SendGrid settings panel.
    """
    try:
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.primitives import hashes
        from cryptography.exceptions import InvalidSignature

        public_key = load_pem_public_key(public_key_pem.encode())
        sig_bytes = base64.b64decode(signature)
        signed_payload = (timestamp + body.decode('utf-8')).encode('utf-8')
        public_key.verify(sig_bytes, signed_payload, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


def _verify_sns_signature(body: dict) -> bool:
    """
    Verify an AWS SNS message RSA-SHA1 signature.

    Downloads the signing certificate from `SigningCertURL` (validated as
    an AWS endpoint), then verifies the canonical string-to-sign.
    Returns False on any verification failure rather than raising.
    """
    try:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes
        from cryptography.x509 import load_pem_x509_certificate
        from cryptography.exceptions import InvalidSignature

        cert_url = body.get('SigningCertURL', '')
        if not _AWS_SNS_URL_RE.match(cert_url):
            logger.error("SNS: rejected cert URL not from AWS: %s", cert_url[:200])
            return False

        cert_pem = urllib.request.urlopen(cert_url, timeout=5).read()
        cert = load_pem_x509_certificate(cert_pem)
        public_key = cert.public_key()

        msg_type = body.get('Type', '')
        fields = _SNS_SIGN_FIELDS.get(msg_type, [])
        string_to_sign = ''.join(
            f'{key}\n{body[key]}\n' for key in fields if key in body
        )

        sig_bytes = base64.b64decode(body.get('Signature', ''))
        public_key.verify(sig_bytes, string_to_sign.encode('utf-8'), padding.PKCS1v15(), hashes.SHA1())
        return True
    except Exception:
        return False


# Event types that should suppress the address
SENDGRID_SUPPRESS_EVENTS = {'bounce', 'spamreport', 'unsubscribe', 'group_unsubscribe'}
MAILGUN_SUPPRESS_EVENTS = {'bounced', 'complained', 'unsubscribed'}
SES_SUPPRESS_TYPES = {'Bounce', 'Complaint'}
RESEND_SUPPRESS_EVENTS = {'email.bounced', 'email.complained'}


def _reason_from_sendgrid(event_type: str) -> str:
    mapping = {
        'bounce': SuppressionReason.BOUNCE_HARD,
        'spamreport': SuppressionReason.COMPLAINT,
        'unsubscribe': SuppressionReason.UNSUBSCRIBE,
        'group_unsubscribe': SuppressionReason.UNSUBSCRIBE,
    }
    return mapping.get(event_type, SuppressionReason.BOUNCE_HARD)


def _reason_from_mailgun(event_type: str) -> str:
    mapping = {
        'bounced': SuppressionReason.BOUNCE_HARD,
        'complained': SuppressionReason.COMPLAINT,
        'unsubscribed': SuppressionReason.UNSUBSCRIBE,
    }
    return mapping.get(event_type, SuppressionReason.BOUNCE_HARD)


def _reason_from_ses(notification_type: str, bounce_type: str = '') -> str:
    if notification_type == 'Complaint':
        return SuppressionReason.COMPLAINT
    if bounce_type == 'Permanent':
        return SuppressionReason.BOUNCE_HARD
    return SuppressionReason.BOUNCE_SOFT


def _verify_resend_signature(
    *,
    secret: str,
    body: bytes,
    message_id: str,
    timestamp: str,
    signature_header: str,
) -> bool:
    """Verify Resend's Standard Webhooks (Svix-compatible) signature."""
    try:
        timestamp_int = int(timestamp)
        if abs(int(time.time()) - timestamp_int) > 300:
            return False

        encoded_secret = secret.removeprefix("whsec_")
        signing_key = base64.b64decode(encoded_secret)
        signed_payload = (
            f"{message_id}.{timestamp}.{body.decode('utf-8')}"
        ).encode("utf-8")
        expected = base64.b64encode(
            hmac.new(signing_key, signed_payload, hashlib.sha256).digest()
        ).decode("ascii")

        signatures = [
            item.split(",", 1)[1]
            for item in signature_header.split()
            if item.startswith("v1,")
        ]
        return any(
            hmac.compare_digest(expected, candidate)
            for candidate in signatures
        )
    except (TypeError, ValueError, UnicodeDecodeError):
        return False


@method_decorator(csrf_exempt, name='dispatch')
class SendgridWebhookView(View):
    """
    Receives SendGrid Event Webhook payloads.
    https://docs.sendgrid.com/for-developers/tracking-events/event

    Validation: ECDSA signature via SendGrid's Event Webhook Security.
    For simplicity this implementation checks the shared verification key;
    replace with full ECDSA verification for production hardening.
    """

    def post(self, request):
        public_key = getattr(settings, 'SENDGRID_WEBHOOK_VERIFICATION_KEY', '')
        if public_key:
            signature = request.headers.get('X-Twilio-Email-Event-Webhook-Signature', '')
            timestamp = request.headers.get('X-Twilio-Email-Event-Webhook-Timestamp', '')
            if not signature or not timestamp:
                logger.warning("SendgridWebhookView: missing signature or timestamp header.")
                return HttpResponseForbidden("Missing signature headers.")
            if not _verify_sendgrid_ecdsa(public_key, request.body, signature, timestamp):
                logger.warning("SendgridWebhookView: ECDSA signature verification failed.")
                return HttpResponseForbidden("Invalid signature.")

        try:
            events = json.loads(request.body)
        except json.JSONDecodeError:
            logger.warning("SendgridWebhookView: invalid JSON body.")
            return HttpResponse(status=400)

        if not isinstance(events, list):
            events = [events]

        for event in events:
            event_type = event.get('event', '')
            email = event.get('email', '').lower().strip()

            # Always record the raw event
            webhook_event = ProviderWebhookEvent.objects.create(
                provider='sendgrid',
                event_type=event_type,
                email=email,
                provider_event_id=event.get('sg_event_id', ''),
                raw_payload=event,
            )

            if event_type in SENDGRID_SUPPRESS_EVENTS and email:
                try:
                    EmailSuppression.suppress(
                        email=email,
                        reason=_reason_from_sendgrid(event_type),
                        provider='sendgrid',
                        provider_event_id=event.get('sg_event_id', ''),
                        raw_payload=event,
                    )
                    webhook_event.mark_processed()
                    logger.info(
                        "SendgridWebhook: suppressed %s reason=%s.",
                        email, event_type,
                    )
                except Exception as exc:
                    webhook_event.mark_failed(str(exc))
                    logger.exception(
                        "SendgridWebhook: failed to suppress %s: %s", email, exc
                    )
            else:
                webhook_event.mark_ignored()

        # SendGrid expects 200 or it will retry
        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class SESWebhookView(View):
    """
    Receives Amazon SES notifications via SNS.
    https://docs.aws.amazon.com/ses/latest/dg/notification-contents.html

    Handles:
    - SubscriptionConfirmation (auto-confirms the SNS subscription)
    - Notification (Bounce / Complaint messages)
    """

    def post(self, request):
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        message_type = body.get('Type', '')

        # Verify AWS SNS message signature before processing any event.
        # This prevents forged Notification bodies from suppressing addresses.
        if not _verify_sns_signature(body):
            logger.error("SESWebhookView: SNS signature verification failed — rejecting message.")
            return HttpResponseForbidden("Invalid SNS message signature.")

        # Auto-confirm SNS subscription.
        # SECURITY: URL already validated as AWS endpoint inside _verify_sns_signature.
        if message_type == 'SubscriptionConfirmation':
            url = body.get('SubscribeURL', '')
            if url and _AWS_SNS_URL_RE.match(url):
                try:
                    urllib.request.urlopen(url)  # noqa: S310
                    logger.info("SESWebhookView: SNS subscription confirmed.")
                except Exception as exc:
                    logger.warning("SESWebhookView: subscription confirm failed: %s", exc)
            elif url:
                logger.error(
                    "SESWebhookView: rejected suspicious SubscribeURL (not an AWS SNS endpoint): %s",
                    url[:200],
                )
            return HttpResponse(status=200)

        if message_type != 'Notification':
            return HttpResponse(status=200)

        try:
            message = json.loads(body.get('Message', '{}'))
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        notification_type = message.get('notificationType', '')

        if notification_type not in SES_SUPPRESS_TYPES:
            return HttpResponse(status=200)

        if notification_type == 'Bounce':
            bounce = message.get('bounce', {})
            bounce_type = bounce.get('bounceType', '')
            recipients = bounce.get('bouncedRecipients', [])
            for r in recipients:
                email = r.get('emailAddress', '').lower().strip()
                if not email:
                    continue
                webhook_event = ProviderWebhookEvent.objects.create(
                    provider='ses',
                    event_type='bounce',
                    email=email,
                    raw_payload=message,
                )
                try:
                    EmailSuppression.suppress(
                        email=email,
                        reason=_reason_from_ses('Bounce', bounce_type),
                        provider='ses',
                        raw_payload=message,
                    )
                    webhook_event.mark_processed()
                    logger.info("SESWebhook: suppressed %s bounce_type=%s.", email, bounce_type)
                except Exception as exc:
                    webhook_event.mark_failed(str(exc))

        elif notification_type == 'Complaint':
            complaint = message.get('complaint', {})
            recipients = complaint.get('complainedRecipients', [])
            for r in recipients:
                email = r.get('emailAddress', '').lower().strip()
                if not email:
                    continue
                webhook_event = ProviderWebhookEvent.objects.create(
                    provider='ses',
                    event_type='complaint',
                    email=email,
                    raw_payload=message,
                )
                try:
                    EmailSuppression.suppress(
                        email=email,
                        reason=SuppressionReason.COMPLAINT,
                        provider='ses',
                        raw_payload=message,
                    )
                    webhook_event.mark_processed()
                    logger.info("SESWebhook: suppressed %s complaint.", email)
                except Exception as exc:
                    webhook_event.mark_failed(str(exc))

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class MailgunWebhookView(View):
    """
    Receives Mailgun webhook events.
    https://documentation.mailgun.com/en/latest/user_manual.html#webhooks

    Validates the request using HMAC-SHA256 over timestamp + token.
    Set MAILGUN_WEBHOOK_SIGNING_KEY in Django settings.
    """

    def post(self, request):
        signing_key = getattr(settings, 'MAILGUN_WEBHOOK_SIGNING_KEY', '')
        if signing_key:
            try:
                data = json.loads(request.body)
                signature_data = data.get('signature', {})
                timestamp = str(signature_data.get('timestamp', ''))
                token = str(signature_data.get('token', ''))
                provided_sig = signature_data.get('signature', '')

                value = timestamp + token
                expected = hmac.new(
                    signing_key.encode(),
                    value.encode(),
                    hashlib.sha256,
                ).hexdigest()

                if not hmac.compare_digest(expected, provided_sig):
                    logger.warning("MailgunWebhookView: invalid signature.")
                    return HttpResponseForbidden("Invalid signature.")
            except Exception:
                return HttpResponse(status=400)
        else:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return HttpResponse(status=400)

        event_data = data.get('event-data', {})
        event_type = event_data.get('event', '')
        email = (
            event_data.get('recipient', '')
            or event_data.get('email', '')
        ).lower().strip()

        webhook_event = ProviderWebhookEvent.objects.create(
            provider='mailgun',
            event_type=event_type,
            email=email,
            provider_event_id=event_data.get('id', ''),
            raw_payload=event_data,
        )

        if event_type in MAILGUN_SUPPRESS_EVENTS and email:
            try:
                EmailSuppression.suppress(
                    email=email,
                    reason=_reason_from_mailgun(event_type),
                    provider='mailgun',
                    provider_event_id=event_data.get('id', ''),
                    raw_payload=event_data,
                )
                webhook_event.mark_processed()
                logger.info("MailgunWebhook: suppressed %s reason=%s.", email, event_type)
            except Exception as exc:
                webhook_event.mark_failed(str(exc))
                logger.exception("MailgunWebhook: failed to suppress %s: %s", email, exc)
        else:
            webhook_event.mark_ignored()

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ResendWebhookView(View):
    """Receive signed Resend delivery events and maintain suppressions."""

    def post(self, request):
        secret = getattr(settings, "RESEND_WEBHOOK_SECRET", "")
        message_id = request.headers.get("svix-id", "")
        timestamp = request.headers.get("svix-timestamp", "")
        signature = request.headers.get("svix-signature", "")

        if not secret:
            logger.error("ResendWebhookView: RESEND_WEBHOOK_SECRET is not configured.")
            return HttpResponseForbidden("Webhook is not configured.")
        if not _verify_resend_signature(
            secret=secret,
            body=request.body,
            message_id=message_id,
            timestamp=timestamp,
            signature_header=signature,
        ):
            logger.warning("ResendWebhookView: signature verification failed.")
            return HttpResponseForbidden("Invalid signature.")

        try:
            event = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse(status=400)

        event_type = event.get("type", "")
        data = event.get("data", {})
        recipients = data.get("to", [])
        if isinstance(recipients, str):
            recipients = [recipients]

        if not recipients:
            ProviderWebhookEvent.objects.create(
                provider="resend",
                event_type=event_type,
                provider_event_id=message_id,
                raw_payload=event,
                status=ProviderWebhookEvent.IGNORED,
            )
            return HttpResponse(status=200)

        for recipient in recipients:
            email = str(recipient).lower().strip()
            webhook_event = ProviderWebhookEvent.objects.create(
                provider="resend",
                event_type=event_type,
                email=email,
                provider_event_id=message_id,
                raw_payload=event,
            )
            if event_type not in RESEND_SUPPRESS_EVENTS or not email:
                webhook_event.mark_ignored()
                continue

            reason = (
                SuppressionReason.COMPLAINT
                if event_type == "email.complained"
                else SuppressionReason.BOUNCE_HARD
            )
            try:
                EmailSuppression.suppress(
                    email=email,
                    reason=reason,
                    provider="resend",
                    provider_event_id=message_id,
                    raw_payload=event,
                )
                webhook_event.mark_processed()
            except Exception as exc:
                webhook_event.mark_failed(str(exc))
                logger.exception(
                    "ResendWebhookView: failed to suppress %s: %s",
                    email,
                    exc,
                )

        return HttpResponse(status=200)

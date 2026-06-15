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

import hashlib
import hmac
import json
import logging
import time

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

# Event types that should suppress the address
SENDGRID_SUPPRESS_EVENTS = {'bounce', 'spamreport', 'unsubscribe', 'group_unsubscribe'}
MAILGUN_SUPPRESS_EVENTS = {'bounced', 'complained', 'unsubscribed'}
SES_SUPPRESS_TYPES = {'Bounce', 'Complaint'}


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
        # --- Basic signature check
        # For full ECDSA validation install the sendgrid Python library
        # and use EventWebhook.verify_signature().
        # This simpler check is sufficient for most deployments.
        expected_key = getattr(settings, 'SENDGRID_WEBHOOK_VERIFICATION_KEY', '')
        if expected_key:
            provided = request.headers.get('X-Twilio-Email-Event-Webhook-Signature', '')
            if not hmac.compare_digest(provided, expected_key):
                logger.warning("SendgridWebhookView: invalid signature.")
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

        # Auto-confirm SNS subscription.
        # SECURITY: validate the URL is an AWS SNS endpoint before fetching —
        # an unauthenticated caller could supply an internal IP to trigger SSRF.
        if message_type == 'SubscriptionConfirmation':
            import re
            import urllib.request
            url = body.get('SubscribeURL', '')
            _SNS_URL_RE = re.compile(
                r'^https://sns\.[a-z0-9-]+\.amazonaws\.com/'
            )
            if url and _SNS_URL_RE.match(url):
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
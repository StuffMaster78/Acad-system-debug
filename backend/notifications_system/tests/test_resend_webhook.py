import base64
import hashlib
import hmac
import json
import time

import pytest
from django.test import override_settings
from django.urls import reverse

from notifications_system.models.email_suppression import (
    EmailSuppression,
    ProviderWebhookEvent,
    SuppressionReason,
)


def _signature(secret: str, body: bytes, message_id: str, timestamp: str) -> str:
    key = base64.b64decode(secret.removeprefix("whsec_"))
    payload = f"{message_id}.{timestamp}.{body.decode()}".encode()
    digest = base64.b64encode(
        hmac.new(key, payload, hashlib.sha256).digest()
    ).decode()
    return f"v1,{digest}"


@pytest.mark.django_db
@override_settings(
    RESEND_WEBHOOK_SECRET="whsec_dGVzdC1zaWduaW5nLWtleQ==",
)
def test_resend_bounce_creates_suppression(client):
    event = {
        "type": "email.bounced",
        "data": {
            "email_id": "email_123",
            "to": ["bounced@example.com"],
        },
    }
    body = json.dumps(event, separators=(",", ":")).encode()
    timestamp = str(int(time.time()))
    message_id = "msg_123"

    response = client.post(
        reverse("notifications:webhook-resend"),
        data=body,
        content_type="application/json",
        headers={
            "svix-id": message_id,
            "svix-timestamp": timestamp,
            "svix-signature": _signature(
                "whsec_dGVzdC1zaWduaW5nLWtleQ==",
                body,
                message_id,
                timestamp,
            ),
        },
    )

    assert response.status_code == 200
    suppression = EmailSuppression.objects.get(email="bounced@example.com")
    assert suppression.reason == SuppressionReason.BOUNCE_HARD
    assert ProviderWebhookEvent.objects.filter(
        provider="resend",
        status=ProviderWebhookEvent.PROCESSED,
    ).exists()


@pytest.mark.django_db
@override_settings(
    RESEND_WEBHOOK_SECRET="whsec_dGVzdC1zaWduaW5nLWtleQ==",
)
def test_resend_webhook_rejects_invalid_signature(client):
    response = client.post(
        reverse("notifications:webhook-resend"),
        data={"type": "email.bounced", "data": {"to": ["x@example.com"]}},
        content_type="application/json",
        headers={
            "svix-id": "msg_bad",
            "svix-timestamp": str(int(time.time())),
            "svix-signature": "v1,invalid",
        },
    )

    assert response.status_code == 403
    assert not ProviderWebhookEvent.objects.exists()

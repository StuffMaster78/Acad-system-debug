from __future__ import annotations

from typing import Any, cast

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from payments_processor.models.webhook_config import WebhookConfig


class WebhookConfigView(APIView):
    """
    GET  — return the current webhook configuration.
    PATCH — update one or more fields (superadmin only).
    """

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [permissions.IsAdminUser()]
        return [permissions.IsAdminUser()]

    def get(self, request: Request) -> Response:
        cfg = WebhookConfig.get()
        return Response(self._serialize(cfg))

    def patch(self, request: Request) -> Response:
        cfg = WebhookConfig.get()
        data = cast(dict[str, Any], request.data)

        if "retry_attempts" in data:
            val = int(data["retry_attempts"])
            if not (0 <= val <= 10):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"retry_attempts": "Must be between 0 and 10."})
            cfg.retry_attempts = val

        if "timeout_seconds" in data:
            val = int(data["timeout_seconds"])
            if not (5 <= val <= 120):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"timeout_seconds": "Must be between 5 and 120."})
            cfg.timeout_seconds = val

        if "signature_verification_enabled" in data:
            cfg.signature_verification_enabled = bool(data["signature_verification_enabled"])

        cfg.updated_by = request.user
        cfg.save()

        return Response(self._serialize(cfg))

    @staticmethod
    def _serialize(cfg: WebhookConfig) -> dict[str, Any]:
        return {
            "retry_attempts": cfg.retry_attempts,
            "timeout_seconds": cfg.timeout_seconds,
            "signature_verification_enabled": cfg.signature_verification_enabled,
            "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None,
        }

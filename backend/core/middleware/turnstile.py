from __future__ import annotations

import json
import logging

import requests
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
PROTECTED_PATHS = {
    "/api/v1/auth/register/",
    "/api/v1/auth/password/reset/request/",
    "/api/v1/auth/magic-link/request/",
    "/api/v1/writer-management/applications/submit/",
    "/cms-api/contact/",
}


class TurnstileMiddleware:
    """Require a valid Turnstile token on anonymous abuse targets."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            getattr(settings, "TURNSTILE_ENABLED", False)
            and request.method == "POST"
            and request.path in PROTECTED_PATHS
        ):
            error = self._validate(request)
            if error:
                return error
        return self.get_response(request)

    @staticmethod
    def _extract_token(request) -> str:
        header_token = request.headers.get("X-Turnstile-Token", "").strip()
        if header_token:
            return header_token

        form_token = request.POST.get("cf-turnstile-response", "").strip()
        if form_token:
            return form_token

        if request.content_type == "application/json":
            try:
                payload = json.loads(request.body or b"{}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                return ""
            return str(
                payload.get("turnstile_token")
                or payload.get("cf-turnstile-response")
                or ""
            ).strip()
        return ""

    def _validate(self, request):
        secret = getattr(settings, "TURNSTILE_SECRET_KEY", "")
        token = self._extract_token(request)
        if not secret:
            logger.error("TURNSTILE_ENABLED is true without a secret key.")
            return JsonResponse(
                {"detail": "Human verification is unavailable."},
                status=503,
            )
        if not token:
            return JsonResponse(
                {"detail": "Human verification is required."},
                status=400,
            )

        try:
            response = requests.post(
                VERIFY_URL,
                data={
                    "secret": secret,
                    "response": token,
                    "remoteip": request.META.get("REMOTE_ADDR", ""),
                },
                timeout=5,
            )
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError):
            logger.exception("Cloudflare Turnstile verification failed.")
            return JsonResponse(
                {"detail": "Human verification could not be completed."},
                status=503,
            )

        if not result.get("success"):
            return JsonResponse(
                {
                    "detail": "Human verification failed.",
                    "error_codes": result.get("error-codes", []),
                },
                status=400,
            )
        return None

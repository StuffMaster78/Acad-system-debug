from __future__ import annotations

import hashlib
import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from privacy.api.serializers.cookie_consent import (
    CookieConsentRecordSerializer,
    CookieConsentWriteSerializer,
)
from privacy.models import CookieConsentRecord, WebsiteCookieConfig


CONSENT_COOKIE_NAME = "writing_system.cookie_consent_id"
# Fallback versions used when no per-tenant WebsiteCookieConfig row exists.
_DEFAULT__DEFAULT_CONSENT_VERSION = "2026-06-15"
_DEFAULT__DEFAULT_POLICY_VERSION  = "2026-06-15"
CONSENT_COOKIE_MAX_AGE = 60 * 60 * 24 * 365


def _hash_value(value: str) -> str:
    if not value:
        return ""
    salt = settings.SECRET_KEY[:32]
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()


def _client_ip(request) -> str:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _anonymous_id_from_request(request) -> uuid.UUID | None:
    raw = (
        request.headers.get("X-Consent-ID")
        or request.COOKIES.get(CONSENT_COOKIE_NAME)
        or request.query_params.get("anonymous_id")
    )
    if not raw:
        return None
    try:
        return uuid.UUID(str(raw))
    except (TypeError, ValueError):
        return None


def _set_consent_cookie(response: Response, anonymous_id: uuid.UUID) -> None:
    response.set_cookie(
        CONSENT_COOKIE_NAME,
        str(anonymous_id),
        max_age=CONSENT_COOKIE_MAX_AGE,
        httponly=False,
        secure=not settings.DEBUG,
        samesite="Lax",
    )


def _latest_consent(request, anonymous_id: uuid.UUID | None):
    website = getattr(request, "website", None)
    queryset = CookieConsentRecord.objects.filter(revoked_at__isnull=True)

    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    if user:
        queryset = queryset.filter(user=user)
    elif anonymous_id:
        queryset = queryset.filter(anonymous_id=anonymous_id)
    else:
        return None

    if website:
        queryset = queryset.filter(website=website)

    return queryset.order_by("-created_at", "-id").first()


def _website_payload(request):
    website = getattr(request, "website", None)
    if not website:
        return None
    return {
        "id": website.id,
        "name": website.name,
        "slug": website.slug,
        "domain": website.domain,
    }


class CookieConfigView(APIView):
    """
    Public host-aware cookie category configuration for banners/modals.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        website = getattr(request, "website", None)
        ga4_id  = getattr(website, "google_analytics_id", None) if website else None

        # Per-tenant config with fallback to platform defaults
        cfg = None
        if website is not None:
            try:
                cfg = WebsiteCookieConfig.objects.get(website=website)
            except WebsiteCookieConfig.DoesNotExist:
                pass

        consent_version    = cfg.consent_version    if cfg else _DEFAULT_CONSENT_VERSION
        policy_version     = cfg.policy_version     if cfg else _DEFAULT_POLICY_VERSION
        privacy_policy_url = cfg.privacy_policy_url if cfg else "/privacy"
        cookie_policy_url  = cfg.cookie_policy_url  if cfg else "/privacy#cookies"
        marketing_available = cfg.marketing_available if cfg else False

        return Response(
            {
                "consent_version": consent_version,
                "policy_version":  policy_version,
                "cookie_name":     CONSENT_COOKIE_NAME,
                "website":         _website_payload(request),
                "categories": [
                    {
                        "key":         "necessary",
                        "label":       "Necessary",
                        "required":    True,
                        "default":     True,
                        "description": (
                            "Required for login, security, checkout, order flow, "
                            "and remembering this consent choice."
                        ),
                    },
                    {
                        "key":         "preferences",
                        "label":       "Preferences",
                        "required":    False,
                        "default":     False,
                        "description": (
                            "Stores convenience choices such as saved form state, "
                            "bookmarks, reactions, and display preferences."
                        ),
                    },
                    {
                        "key":         "analytics",
                        "label":       "Analytics",
                        "required":    False,
                        "default":     False,
                        "description": (
                            "Helps us understand page usage, funnels, and content "
                            "performance through aggregated analytics."
                        ),
                    },
                    {
                        "key":         "marketing",
                        "label":       "Marketing",
                        "required":    False,
                        "default":     False,
                        "description": (
                            "Allows campaign attribution, promotional measurement, "
                            "and advertising integrations where enabled."
                        ),
                    },
                ],
                "integrations": {
                    "ga4_measurement_id":  ga4_id or None,
                    "analytics_available": bool(ga4_id),
                    "marketing_available": marketing_available,
                },
                "links": {
                    "privacy_policy": privacy_policy_url,
                    "cookie_policy":  cookie_policy_url,
                },
            }
        )


class CookieConsentCurrentView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        anonymous_id = _anonymous_id_from_request(request)
        record = _latest_consent(request, anonymous_id)
        if not record:
            return Response(
                {
                    "has_consent": False,
                    "anonymous_id": str(anonymous_id) if anonymous_id else None,
                    "consent": None,
                }
            )

        response = Response(
            {
                "has_consent": True,
                "anonymous_id": str(record.anonymous_id),
                "consent": CookieConsentRecordSerializer(record).data,
            }
        )
        _set_consent_cookie(response, record.anonymous_id)
        return response


class CookieConsentView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = CookieConsentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        anonymous_id = data.get("anonymous_id") or _anonymous_id_from_request(request) or uuid.uuid4()
        website = getattr(request, "website", None)
        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

        record = CookieConsentRecord.objects.create(
            website=website,
            user=user,
            anonymous_id=anonymous_id,
            consent_version=data.get("consent_version", _DEFAULT_CONSENT_VERSION),
            policy_version=data.get("policy_version", _DEFAULT_POLICY_VERSION),
            necessary=True,
            preferences=data["preferences"],
            analytics=data["analytics"],
            marketing=data["marketing"],
            source=data["source"],
            source_host=request.get_host().split(":")[0],
            ip_hash=_hash_value(_client_ip(request)),
            user_agent_hash=_hash_value(request.META.get("HTTP_USER_AGENT", "")),
        )

        response = Response(
            {
                "anonymous_id": str(record.anonymous_id),
                "consent": CookieConsentRecordSerializer(record).data,
            },
            status=status.HTTP_201_CREATED,
        )
        _set_consent_cookie(response, record.anonymous_id)
        return response


class CookieConsentRevokeView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        anonymous_id = _anonymous_id_from_request(request)
        website = getattr(request, "website", None)

        queryset = CookieConsentRecord.objects.filter(revoked_at__isnull=True)
        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        if user:
            queryset = queryset.filter(user=user)
        elif anonymous_id:
            queryset = queryset.filter(anonymous_id=anonymous_id)
        else:
            return Response(
                {
                    "revoked": 0,
                    "anonymous_id": None,
                    "consent": None,
                }
            )

        if website:
            queryset = queryset.filter(website=website)

        revoked = queryset.update(revoked_at=timezone.now(), updated_at=timezone.now())
        if not anonymous_id:
            anonymous_id = uuid.uuid4()

        record = CookieConsentRecord.objects.create(
            website=website,
            user=user,
            anonymous_id=anonymous_id,
            consent_version=_DEFAULT_CONSENT_VERSION,
            policy_version=_DEFAULT_POLICY_VERSION,
            necessary=True,
            preferences=False,
            analytics=False,
            marketing=False,
            source=CookieConsentRecord.SOURCE_SETTINGS,
            source_host=request.get_host().split(":")[0],
            ip_hash=_hash_value(_client_ip(request)),
            user_agent_hash=_hash_value(request.META.get("HTTP_USER_AGENT", "")),
        )

        response = Response(
            {
                "revoked": revoked,
                "anonymous_id": str(record.anonymous_id),
                "consent": CookieConsentRecordSerializer(record).data,
            }
        )
        _set_consent_cookie(response, record.anonymous_id)
        return response

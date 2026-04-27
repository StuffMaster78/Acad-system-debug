from __future__ import annotations

import json
import logging
from typing import Any, Optional, cast

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils.timezone import now

from audit_logging.models import AuditLogEntry, WebhookAuditLog
from audit_logging.tasks import async_log_audit
from audit_logging.utils import (
    get_client_ip,
    get_current_request,
    get_user_agent,
)

logger = logging.getLogger("audit")


class AuditLogService:
    """
    Service for creating audit log entries safely and consistently.

    Design goals:
        1. Keep sync and async logging payloads identical.
        2. Avoid leaking secrets into audit logs.
        3. Avoid large payloads bloating storage.
        4. Never let audit failures break core business flows.
        5. Make future scaling easier.
    """

    DEFAULT_USER_AGENT = "Unknown Agent"

    SENSITIVE_KEYS = {
        "password",
        "pass",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "api_key",
        "authorization",
        "cookie",
        "sessionid",
        "otp",
        "recovery_code",
        "recovery_codes",
        "cvv",
        "card_number",
        "pin",
    }

    MAX_METADATA_BYTES = 32_000
    MAX_CHANGES_BYTES = 64_000
    MAX_NOTES_LENGTH = 4_000
    TRUNCATED_MARKER = "[TRUNCATED]"

    @classmethod
    def log(
        cls,
        *,
        website,
        action: str,
        actor=None,
        target=None,
        metadata: Optional[dict[str, Any]] = None,
        changes: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        notes: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> AuditLogEntry:
        """
        Create an audit log entry synchronously.
        """
        payload = cls._normalize_payload(
            website=AuditLogEntry.website,
            action=action,
            actor=actor,
            target=target,
            metadata=metadata,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            notes=notes,
            request_id=request_id,
        )
        return cls._write_log(**payload)

    @classmethod
    def log_auto(
        cls,
        *,
        website,
        action: str,
        actor=None,
        target=None,
        metadata: Optional[dict[str, Any]] = None,
        changes: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        notes: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> AuditLogEntry | None:
        """
        Automatically log audit entry async or sync.

        Async dispatch happens on transaction commit so workers do not race
        ahead of uncommitted database changes.
        """
        payload = cls._normalize_payload(
            website=website,
            action=action,
            actor=actor,
            target=target,
            metadata=metadata,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            notes=notes,
            request_id=request_id,
        )

        use_async = getattr(settings, "USE_ASYNC_AUDIT_LOGGING", False)

        if use_async:
            try:
                task = cast(Any, async_log_audit)

                def enqueue_audit_log() -> None:
                    task.delay(**payload)

                transaction.on_commit(enqueue_audit_log)
                return None
            except Exception as exc:
                logger.warning(
                    (
                        "[AUDIT] Async dispatch failed. "
                        "action=%s actor_id=%s target=%s error=%s"
                    ),
                    payload["action"],
                    payload["actor_id"],
                    payload["target"],
                    str(exc),
                    exc_info=True,
                )

        try:
            return cls._write_log(**payload)
        except Exception as exc:
            logger.exception(
                (
                    "[AUDIT] Sync write failed. "
                    "action=%s actor_id=%s target=%s error=%s"
                ),
                payload["action"],
                payload["actor_id"],
                payload["target"],
                str(exc),
            )
            return None

    @classmethod
    def log_from_signal(
        cls,
        *,
        action: str,
        sender: type[models.Model],
        instance: models.Model,
        user=None,
        request=None,
    ) -> AuditLogEntry | None:
        """
        Wrapper for generic model signal usage.
        """
        model_name = sender.__name__
        app_label = sender._meta.app_label
        event_message = f"{model_name} was {action.lower()}."

        ip_address = get_client_ip(request) if request else None
        user_agent = get_user_agent(request) if request else None

        return cls.log_auto(
            website=AuditLogEntry.website,
            action=action,
            actor=user,
            target=instance,
            metadata={
                "event": "model_signal",
                "model": model_name,
                "app_label": app_label,
                "message": event_message,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    def _normalize_payload(
        cls,
        *,
        website,
        action: str,
        actor=None,
        target=None,
        metadata: Optional[dict[str, Any]] = None,
        changes: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        notes: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Normalize, sanitize, and constrain audit payload.
        """
        resolved_actor = cls._resolve_actor(actor)
        resolved_request = cls._resolve_request()

        resolved_ip, resolved_agent = cls._resolve_request_context(
            request=resolved_request,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        target_data = cls._normalize_target(target)

        safe_metadata = cls._truncate_json_payload(
            cast(dict[str, Any], cls._sanitize_value(metadata or {})),
            max_bytes=cls.MAX_METADATA_BYTES,
            field_name="metadata",
        )
        safe_changes = cls._truncate_json_payload(
            cast(dict[str, Any], cls._sanitize_value(changes or {})),
            max_bytes=cls.MAX_CHANGES_BYTES,
            field_name="changes",
        )
        safe_notes = cls._truncate_text(
            notes or "",
            max_length=cls.MAX_NOTES_LENGTH,
        )

        if not request_id and resolved_request is not None:
            request_id = getattr(resolved_request, "request_id", None)

        return {
            "action": action,
            "actor_id": getattr(resolved_actor, "pk", None),
            "target": target_data["target"],
            "target_id": target_data["target_id"],
            "metadata": safe_metadata,
            "changes": safe_changes,
            "ip_address": resolved_ip,
            "user_agent": resolved_agent,
            "notes": safe_notes,
            "request_id": request_id,
            "timestamp": now(),
            "target_content_type_id": target_data["target_content_type_id"],
            "target_object_id": target_data["target_object_id"],
        }

    @classmethod
    def _write_log(
        cls,
        *,
        action: str,
        actor_id: Optional[int],
        target: str,
        target_id: Optional[int],
        metadata: dict[str, Any],
        changes: dict[str, Any],
        ip_address: Optional[str],
        user_agent: Optional[str],
        notes: str,
        request_id: Optional[str],
        timestamp,
        target_content_type_id: Optional[int],
        target_object_id: Optional[int],
    ) -> AuditLogEntry:
        """
        Persist an audit log entry.
        """
        return AuditLogEntry.objects.create(
            action=action,
            actor_id=actor_id,
            target=target,
            target_id=target_id,
            metadata=metadata,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            notes=notes,
            request_id=request_id,
            timestamp=timestamp,
            target_content_type_id=target_content_type_id,
            target_object_id=target_object_id,
        )

    @classmethod
    def _resolve_actor(cls, actor):
        """
        Resolve actor from explicit value or request context.
        """
        if actor is not None:
            return actor

        request = cls._resolve_request()
        if request is None or not hasattr(request, "user"):
            return None

        user = request.user
        if getattr(user, "is_authenticated", False):
            return user
        return None

    @classmethod
    def _resolve_request(cls):
        """
        Safely resolve the current request from request local context.
        """
        try:
            return get_current_request()
        except Exception as exc:
            logger.debug(
                "[AUDIT] Could not resolve current request: %s",
                str(exc),
                exc_info=True,
            )
            return None

    @classmethod
    def _resolve_request_context(
        cls,
        *,
        request=None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> tuple[Optional[str], str]:
        """
        Resolve IP address and user agent with safe fallbacks.
        """
        resolved_ip = ip_address
        resolved_agent = user_agent

        if resolved_ip is None:
            try:
                resolved_ip = get_client_ip(request)
            except Exception as exc:
                logger.debug(
                    "[AUDIT] Could not resolve client IP: %s",
                    str(exc),
                    exc_info=True,
                )
                resolved_ip = None

        if resolved_agent is None:
            try:
                resolved_agent = get_user_agent(request)
            except Exception as exc:
                logger.debug(
                    "[AUDIT] Could not resolve user agent: %s",
                    str(exc),
                    exc_info=True,
                )
                resolved_agent = None

        return resolved_ip, resolved_agent or cls.DEFAULT_USER_AGENT

    @classmethod
    def _normalize_target(cls, target: Any) -> dict[str, Any]:
        """
        Normalize target object into durable audit fields.
        """
        target_str = ""
        target_id: int | None = None
        target_content_type_id: int | None = None
        target_object_id: int | None = None

        if target is None:
            return {
                "target": target_str,
                "target_id": target_id,
                "target_content_type_id": target_content_type_id,
                "target_object_id": target_object_id,
            }

        if target is not None and hasattr(target, "_meta"):
            target_obj = cast(Any, target)
            model_class = target_obj.__class__
            target_str = (
                f"{target_obj._meta.app_label}.{model_class.__name__}"
            )
            target_pk = getattr(target_obj, "pk", None)
            target_id = target_pk
            target_object_id = target_pk

            try:
                content_type = ContentType.objects.get_for_model(
                    model_class,
                    for_concrete_model=False,
                )
                target_content_type_id = content_type.pk
            except Exception as exc:
                logger.warning(
                    "[AUDIT] Failed to resolve ContentType for target=%s: %s",
                    target_str,
                    str(exc),
                    exc_info=True,
                )

        elif isinstance(target, str):
            target_str = target
        else:
            target_str = str(target)

        return {
            "target": target_str,
            "target_id": target_id,
            "target_content_type_id": target_content_type_id,
            "target_object_id": target_object_id,
        }

    @classmethod
    def _sanitize_value(cls, value: Any) -> Any:
        """
        Recursively sanitize structured payloads to avoid storing secrets.
        """
        if isinstance(value, dict):
            sanitized: dict[str, Any] = {}
            for key, item in value.items():
                key_str = str(key).lower()
                if key_str in cls.SENSITIVE_KEYS:
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = cls._sanitize_value(item)
            return sanitized

        if isinstance(value, list):
            return [cls._sanitize_value(item) for item in value]

        if isinstance(value, tuple):
            return [cls._sanitize_value(item) for item in value]

        return value

    @classmethod
    def _truncate_json_payload(
        cls,
        payload: dict[str, Any],
        *,
        max_bytes: int,
        field_name: str,
    ) -> dict[str, Any]:
        """
        Truncate oversized JSON payloads safely.
        """
        try:
            encoded = json.dumps(payload, default=str, ensure_ascii=False)
        except Exception as exc:
            logger.warning(
                "[AUDIT] Failed to JSON encode %s payload: %s",
                field_name,
                str(exc),
                exc_info=True,
            )
            return {
                "truncated": True,
                "reason": "serialization_failed",
                "field": field_name,
            }

        if len(encoded.encode("utf-8")) <= max_bytes:
            return payload

        logger.warning(
            "[AUDIT] %s payload exceeded size limit and was truncated",
            field_name,
        )
        return {
            "truncated": True,
            "reason": "size_limit_exceeded",
            "field": field_name,
            "preview": encoded[:2000],
            "max_bytes": max_bytes,
        }

    @classmethod
    def _truncate_text(cls, value: str, *, max_length: int) -> str:
        """
        Truncate oversized text values by character length.
        """
        if len(value) <= max_length:
            return value
        return value[:max_length] + cls.TRUNCATED_MARKER


class WebhookAuditLogger:
    """
    Service for logging webhook events safely.
    """

    MAX_PAYLOAD_BYTES = 64_000
    MAX_RESPONSE_BODY_BYTES = 64_000
    TRUNCATED_MARKER = "[TRUNCATED]"

    @classmethod
    def log_webhook_event(
        cls,
        *,
        user,
        platform,
        webhook_url,
        event,
        order_id,
        payload,
        response_body,
        response_status,
        was_successful,
        is_test: bool = False,
        fallback_icon=None,
    ) -> WebhookAuditLog:
        safe_payload = cls._truncate_json_payload(
            cast(
                dict[str, Any],
                AuditLogService._sanitize_value(payload or {}),
            ),
            max_bytes=cls.MAX_PAYLOAD_BYTES,
            field_name="webhook_payload",
        )

        safe_response_body = cls._truncate_text_by_bytes(
            response_body or "",
            max_bytes=cls.MAX_RESPONSE_BODY_BYTES,
        )

        return WebhookAuditLog.objects.create(
            user=user,
            platform=platform,
            webhook_url=webhook_url,
            event=event,
            order_id=order_id,
            payload=safe_payload,
            response_body=safe_response_body,
            response_status=response_status,
            was_successful=was_successful,
            is_test=is_test,
            fallback_icon=fallback_icon,
        )

    @staticmethod
    def _truncate_json_payload(
        payload: dict[str, Any],
        *,
        max_bytes: int,
        field_name: str,
    ) -> dict[str, Any]:
        try:
            encoded = json.dumps(payload, default=str, ensure_ascii=False)
        except Exception:
            return {
                "truncated": True,
                "reason": "serialization_failed",
                "field": field_name,
            }

        if len(encoded.encode("utf-8")) <= max_bytes:
            return payload

        return {
            "truncated": True,
            "reason": "size_limit_exceeded",
            "field": field_name,
            "preview": encoded[:2000],
            "max_bytes": max_bytes,
        }

    @classmethod
    def _truncate_text_by_bytes(
        cls,
        value: str,
        *,
        max_bytes: int,
    ) -> str:
        encoded = value.encode("utf-8")
        if len(encoded) <= max_bytes:
            return value
        truncated = encoded[:max_bytes].decode("utf-8", errors="ignore")
        return truncated + cls.TRUNCATED_MARKER
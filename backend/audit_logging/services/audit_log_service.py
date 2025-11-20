import logging
from typing import Optional

from django.conf import settings
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType

from audit_logging.models import AuditLogEntry, WebhookAuditLog
from audit_logging.tasks import async_log_audit
from audit_logging.utils import get_current_request, get_client_ip, get_user_agent

logger = logging.getLogger("audit")


class AuditLogService:
    """ Service for handling audit log entries."""
    @classmethod
    def log(
        cls,
        *,
        action: str,
        actor=None,
        target=None,
        metadata: Optional[dict] = None,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        notes: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> AuditLogEntry:
        """
        Logs an audit action synchronously.
        """
        target_str = None
        target_id = None
        target_content_type = None
        target_object_id = None

        if target and hasattr(target, "_meta"):
            target_str = f"{target._meta.app_label}.{target.__class__.__name__}"
            target_id = target.pk
            target_content_type = ContentType.objects.get_for_model(target.__class__)
            target_object_id = target.pk
        elif isinstance(target, str):
            target_str = target
            target_id = None

        # Ensure ip/user_agent always have safe defaults
        if not ip_address or not user_agent:
            try:
                req = get_current_request()
            except Exception:
                req = None
            if not ip_address:
                try:
                    ip_address = get_client_ip(req)
                except Exception:
                    ip_address = None
            if not user_agent:
                try:
                    user_agent = get_user_agent(req)
                except Exception:
                    user_agent = None

        ip_address = ip_address or None  # Use None instead of "Unknown IP" for GenericIPAddressField
        user_agent = user_agent or "Unknown Agent"

        # Ensure non-nullable fields
        safe_target = target_str or ""

        return AuditLogEntry.objects.create(
            action=action,
            actor=actor,
            target=safe_target,
            target_id=target_id,
            metadata=metadata or {},
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent,
            notes=notes or "",
            request_id=request_id,
            timestamp=now(),
            target_content_type=target_content_type,
            target_object_id=target_object_id,
        )

    @classmethod
    def log_auto(
        cls,
        *,
        action: str,
        target=None,
        actor=None,
        metadata: Optional[dict] = None,
    ):
        """
        Automatically decides whether to log audit entry async or sync.
        """
        request = get_current_request()
        use_async = getattr(settings, "USE_ASYNC_AUDIT_LOGGING", False)

        if not actor and request and hasattr(request, "user"):
            user = request.user
            actor = user if user.is_authenticated else None

        ip = get_client_ip(request)
        agent = get_user_agent(request)

        if use_async:
            try:
                user_id = actor.id if actor else None
                target_str = (
                    f"{target._meta.app_label}.{target.__class__.__name__}"
                    if hasattr(target, "_meta")
                    else str(target)
                )
                target_id = getattr(target, "pk", None)

                return async_log_audit.delay(
                    action=action,
                    target=target_str,
                    target_id=target_id,
                    actor_id=user_id,
                    metadata=metadata or {},
                    ip_address=ip,
                    user_agent=agent,
                )
            except Exception as e:
                logger.warning("[AUDIT] Async logging failed: %s", str(e))

        return cls.log(
            action=action,
            actor=actor,
            target=target,
            metadata=metadata,
            ip_address=ip,
            user_agent=agent,
        )

    @classmethod
    def log_from_signal(
        cls,
        *,
        action,
        sender,
        instance,
        user=None,
        request=None,
    ):
        """
        Wrapper for model signal usage.
        """
        from audit_logging.utils import get_client_ip, get_user_agent

        model_name = sender.__name__
        app_label = sender._meta.app_label

        return cls.log(
            action=action,
            actor=user,
            target=instance,
            metadata={"message": f"{model_name} was {action.lower()}d."},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    

class WebhookAuditLogger:
    """ 
    Service for logging webhook events.
    Usage:
        WebhookAuditLogger.log_webhook_event(
            user=user,
            platform=platform,
            webhook_url=webhook_url,
            event=event,
            order_id=order_id,
            payload=payload,
            response_body=response_body,
            response_status=response_status,
            was_successful=was_successful,
            is_test=is_test,
            fallback_icon=fallback_icon,
        )
    """

    @staticmethod
    def log_webhook_event(
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
        is_test=False,
        fallback_icon=None,
    ):
        WebhookAuditLog.objects.create(
            user=user,
            platform=platform,
            webhook_url=webhook_url,
            event=event,
            order_id=order_id,
            payload=payload,
            response_body=response_body,
            response_status=response_status,
            was_successful=was_successful,
            is_test=is_test,
            fallback_icon=fallback_icon,
        )
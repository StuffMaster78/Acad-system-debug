"""
Audit signals for authentication and user-state events.
High-value, always sensitive: login, logout, role change, suspension, deletion.
"""
from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from audit_logging.factories.audit_event_factory import AuditEventFactory

log = logging.getLogger("audit")
User = get_user_model()


def _website(user):
    return getattr(user, "website", None)


def _actor_meta(user):
    return {
        "actor_role": getattr(user, "role", ""),
        "actor_display": user.get_full_name() or user.username,
    }


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    try:
        AuditEventFactory.create(
            action="auth.login",
            website=_website(user),
            actor_id=user.pk,
            actor_role=getattr(user, "role", ""),
            actor_display=user.get_full_name() or user.username,
            object_type="user",
            object_id=str(user.pk),
            metadata={
                "ip": getattr(request, "META", {}).get("REMOTE_ADDR"),
                "user_agent": getattr(request, "META", {}).get("HTTP_USER_AGENT", "")[:256],
            },
            severity="info",
            service_name="auth",
        )
    except Exception:
        log.exception("audit_login failed")


@receiver(user_logged_out)
def audit_logout(sender, request, user, **kwargs):
    if not user:
        return
    try:
        AuditEventFactory.create(
            action="auth.logout",
            website=_website(user),
            actor_id=user.pk,
            actor_role=getattr(user, "role", ""),
            actor_display=user.get_full_name() or user.username,
            object_type="user",
            object_id=str(user.pk),
            severity="info",
            service_name="auth",
        )
    except Exception:
        log.exception("audit_logout failed")


@receiver(post_save, sender=User)
def audit_user_role_changed(sender, instance, created, **kwargs):
    """
    Detect role changes by comparing to the database snapshot.
    Only fires on update (not create) when role is actually different.
    """
    if created:
        return
    try:
        prev = User.objects.filter(pk=instance.pk).values("role", "is_active", "is_suspended").first()
        if prev is None:
            return

        new_role = getattr(instance, "role", None)
        old_role = prev.get("role")
        if old_role != new_role:
            AuditEventFactory.create(
                action="auth.role_changed",
                website=_website(instance),
                actor_id=None,
                object_type="user",
                object_id=str(instance.pk),
                before={"role": old_role},
                after={"role": new_role},
                metadata={
                    "user_email": instance.email,
                    **_actor_meta(instance),
                },
                severity="warning",
                is_sensitive=True,
                sensitivity_level="role_change",
                service_name="auth",
            )
    except Exception:
        log.exception("audit_user_role_changed failed")


@receiver(post_save, sender=User)
def audit_user_suspension(sender, instance, created, **kwargs):
    if created:
        return
    try:
        prev = User.objects.filter(pk=instance.pk).values("is_active").first()
        if prev is None:
            return
        was_active = prev.get("is_active", True)
        is_now_active = getattr(instance, "is_active", True)
        if was_active and not is_now_active:
            AuditEventFactory.create(
                action="auth.user_suspended",
                website=_website(instance),
                object_type="user",
                object_id=str(instance.pk),
                metadata={
                    "user_email": instance.email,
                    "role": getattr(instance, "role", ""),
                },
                severity="warning",
                is_sensitive=True,
                sensitivity_level="account_state_change",
                service_name="auth",
            )
    except Exception:
        log.exception("audit_user_suspension failed")

# notifications_system/services/dispatch.py
# -*- coding: utf-8 -*-
"""Legacy dispatch shim.

Prefer calling NotificationService directly:
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(...)

This module exists to keep older imports working while you migrate.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Union
import warnings


def send(
    *,
    user,
    event: str,
    payload: Optional[Dict[str, Any]] = None,
    website=None,
    actor=None,
    channels: Optional[Iterable[str]] = None,
    category: Optional[str] = None,
    template_name: Optional[str] = None,
    priority: Union[int, str] = 5,
    priority_label: Optional[str] = None,
    is_critical: bool = False,
    is_digest: bool = False,
    digest_group: Optional[str] = None,
    is_silent: bool = False,
    email_override: Optional[str] = None,
    global_broadcast: bool = False,
    groups: Optional[Iterable[str]] = None,
    role: Optional[str] = None,
):
    """Send a notification via the core service (legacy wrapper).

    Args:
        user: Target user (must be authenticated).
        event: Canonical event key (e.g., "order.created").
        payload: Optional event context.
        website: Tenant/site object.
        actor: Optional actor who triggered the event.
        channels: Explicit channels to send on.
        category: Arbitrary category string.
        template_name: Optional render skin hint.
        priority: Integer or label for priority.
        priority_label: Legacy label kept for back-compat.
        is_critical: If True, may bypass mute.
        is_digest: If True, mark for digest grouping.
        digest_group: Explicit digest group key.
        is_silent: If True, persist but do not deliver.
        email_override: Override recipient email.
        global_broadcast: Publish to global stream.
        groups: Optional SSE/polling groups.
        role: Optional role for role-channel mapping.

    Returns:
        The return value of NotificationService.send_notification
        (usually a Notification instance, a broadcast object, or None).
    """
    warnings.warn(
        "notifications_system.services.dispatch.send is deprecated; "
        "use NotificationService.send_notification instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    from .core import NotificationService  # lazy to avoid import cycles

    return NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=website,
        actor=actor,
        channels=list(channels) if channels else None,
        category=category,
        template_name=template_name,
        priority=priority,
        priority_label=priority_label,
        is_critical=is_critical,
        is_digest=is_digest,
        digest_group=digest_group,
        is_silent=is_silent,
        email_override=email_override,
        global_broadcast=global_broadcast,
        groups=groups,
        role=role,
    )


def broadcast(
    *,
    event: str,
    title: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    website=None,
    channels: Optional[Iterable[str]] = None,
    priority: int = 5,
):
    """Create a broadcast and fan out (legacy wrapper).

    Args:
        event: Broadcast event key.
        title: Broadcast title.
        message: Broadcast message.
        context: Optional context.
        website: Tenant/site object.
        channels: Channels to use (defaults handled in core).
        priority: Integer priority.

    Returns:
        The BroadcastNotification created by the core service.
    """
    warnings.warn(
        "notifications_system.services.dispatch.broadcast is deprecated; "
        "use NotificationService.send_broadcast instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    from .core import NotificationService

    return NotificationService.send_broadcast(
        event=event,
        title=title,
        message=message,
        context=context or {},
        website=website,
        channels=channels,
        priority=priority,
    )


def send_digests(group: str, since=None):
    """Send digest notifications (legacy wrapper).

    Args:
        group: Digest group key.
        since: Optional datetime lower bound.

    Returns:
        Queryset or list returned by the core digest sender.
    """
    warnings.warn(
        "notifications_system.services.dispatch.send_digests is "
        "deprecated; use NotificationService.send_digests instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    from .core import NotificationService

    return NotificationService.send_digests(group, since=since)

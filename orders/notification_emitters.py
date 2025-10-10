# orders/notification_emitters.py
from __future__ import annotations

from typing import Any, Mapping, Optional, Dict

from django.utils import timezone

from notifications_system.registry.handler_registry import dispatch

try:
    # Prefer your richer, app-specific context builder if present.
    from .notification_context import build_order_context as _build_ctx
except ModuleNotFoundError:  # pragma: no cover
    _build_ctx = None  # type: ignore[assignment]


def _default_ctx(order: Any,
                 *,
                 actor: Any | None = None,
                 extra: Optional[Mapping[str, Any]] = None
                 ) -> Dict[str, Any]:
    """Build a minimal, serializable context for notifications.

    Args:
        order: Order-like instance with common attributes.
        actor: User or system actor who caused the event.
        extra: Optional extra fields to shallow-merge into the context.

    Returns:
        dict: Context payload safe to serialize to JSON.
    """
    website = getattr(order, "website", None)
    client = getattr(order, "client", None)
    writer = getattr(order, "writer", None)

    deadline = getattr(order, "deadline_at", None)
    if hasattr(deadline, "isoformat"):
        deadline_iso = deadline.isoformat()
    else:
        deadline_iso = None

    ctx: Dict[str, Any] = {
        "now": timezone.now().isoformat(),
        "order": {
            "id": getattr(order, "id", None),
            "number": getattr(order, "number", None),
            "topic": getattr(order, "topic", None),
            "status": getattr(order, "status", None),
            "deadline_at": deadline_iso,
            "price": getattr(order, "price", None),
            "currency": getattr(order, "currency", None),
        },
        "website": {
            "id": getattr(website, "id", None),
            "name": getattr(website, "name", None),
            "domain": getattr(website, "domain", None),
        } if website else {},
        "client": {
            "id": getattr(client, "id", None),
            "email": getattr(client, "email", None),
            "name": getattr(client, "get_full_name", lambda: None)(),
        } if client else {},
        "writer": {
            "id": getattr(writer, "id", None),
            "email": getattr(writer, "email", None),
            "name": getattr(writer, "get_full_name", lambda: None)(),
        } if writer else {},
        "actor": {
            "id": getattr(actor, "id", None),
            "email": getattr(actor, "email", None),
            "name": getattr(actor, "get_full_name", lambda: None)(),
        } if actor else {},
    }
    if extra:
        ctx.update(dict(extra))
    return ctx


def _context(event_key: str,
             order: Any,
             *,
             actor: Any | None = None,
             extra: Optional[Mapping[str, Any]] = None
             ) -> Dict[str, Any]:
    """Return the app-level context (prefers custom builder if available).

    Args:
        event_key: Canonical event key (e.g., "order.paid").
        order: Order-like object.
        actor: User or system actor who caused the event.
        extra: Optional extra fields to merge.

    Returns:
        dict: Context payload.
    """
    if callable(_build_ctx):
        base = _build_ctx(
            event=event_key,
            order=order,
            actor=actor,
            website=getattr(order, "website", None),
        )
        if extra:
            base.update(dict(extra))
        return base
    return _default_ctx(order, actor=actor, extra=extra)


def emit_event(event_key: str,
               *,
               order: Any,
               actor: Any | None = None,
               extra: Optional[Mapping[str, Any]] = None) -> None:
    """Emit a canonical order event into the notifications pipeline.

    This calls the handler registry, which resolves recipients by role
    and sends via the NotificationService.

    Args:
        event_key: Canonical event (e.g., "order.paid").
        order: Order-like object for context.
        actor: Optional user/system actor.
        extra: Optional additional context fields.

    Returns:
        None
    """
    ctx = _context(event_key, order, actor=actor, extra=extra)
    dispatch(event_key, ctx)


# ---- Convenience emitters (one per transition) -----------------------------

def emit_order_unpaid(*, order: Any, actor: Any | None = None,
                      extra: Mapping[str, Any] | None = None) -> None:
    """Order marked as unpaid or invoice issued."""
    emit_event("order.unpaid", order=order, actor=actor, extra=extra)


def emit_order_paid(*, order: Any, actor: Any | None = None,
                    extra: Mapping[str, Any] | None = None) -> None:
    """Payment received."""
    emit_event("order.paid", order=order, actor=actor, extra=extra)


def emit_order_available(*, order: Any, actor: Any | None = None,
                         extra: Mapping[str, Any] | None = None) -> None:
    """Order available in the pool for assignment."""
    emit_event("order.available", order=order, actor=actor, extra=extra)


def emit_order_in_progress(*, order: Any, actor: Any | None = None,
                           extra: Mapping[str, Any] | None = None) -> None:
    """Work started / in_progress."""
    emit_event("order.in_progress", order=order, actor=actor, extra=extra)


def emit_order_on_hold(*, order: Any, actor: Any | None = None,
                       extra: Mapping[str, Any] | None = None) -> None:
    """Order put on hold."""
    emit_event("order.on_hold", order=order, actor=actor, extra=extra)


def emit_order_submitted(*, order: Any, actor: Any | None = None,
                         extra: Mapping[str, Any] | None = None) -> None:
    """Writer submitted work for review."""
    emit_event("order.submitted", order=order, actor=actor, extra=extra)


def emit_order_reviewed(*, order: Any, actor: Any | None = None,
                        extra: Mapping[str, Any] | None = None) -> None:
    """Client/QA reviewed the submission."""
    emit_event("order.reviewed", order=order, actor=actor, extra=extra)


def emit_order_revision_requested(
        *, order: Any, actor: Any | None = None,
        extra: Mapping[str, Any] | None = None) -> None:
    """Client requested a revision."""
    emit_event("order.revision_requested", order=order, actor=actor,
               extra=extra)


def emit_order_revision_in_progress(
        *, order: Any, actor: Any | None = None,
        extra: Mapping[str, Any] | None = None) -> None:
    """Writer started revision work."""
    emit_event("order.revision_in_progress", order=order, actor=actor,
               extra=extra)


def emit_order_revised(*, order: Any, actor: Any | None = None,
                       extra: Mapping[str, Any] | None = None) -> None:
    """Revised work submitted."""
    emit_event("order.revised", order=order, actor=actor, extra=extra)


def emit_order_returned(*, order: Any, actor: Any | None = None,
                        extra: Mapping[str, Any] | None = None) -> None:
    """Submission returned outside revision flow."""
    emit_event("order.returned", order=order, actor=actor, extra=extra)


def emit_order_rated(*, order: Any, actor: Any | None = None,
                     extra: Mapping[str, Any] | None = None) -> None:
    """Client rated the order."""
    emit_event("order.rated", order=order, actor=actor, extra=extra)


def emit_order_approved(*, order: Any, actor: Any | None = None,
                        extra: Mapping[str, Any] | None = None) -> None:
    """Client/QA approved the order."""
    emit_event("order.approved", order=order, actor=actor, extra=extra)


def emit_order_refunded(*, order: Any, actor: Any | None = None,
                        extra: Mapping[str, Any] | None = None) -> None:
    """Order refunded (full or partial)."""
    emit_event("order.refunded", order=order, actor=actor, extra=extra)


def emit_order_cancelled(*, order: Any, actor: Any | None = None,
                         extra: Mapping[str, Any] | None = None) -> None:
    """Order cancelled."""
    emit_event("order.cancelled", order=order, actor=actor, extra=extra)


def emit_order_archived(*, order: Any, actor: Any | None = None,
                        extra: Mapping[str, Any] | None = None) -> None:
    """Order archived for housekeeping."""
    emit_event("order.archived", order=order, actor=actor, extra=extra)


def emit_order_completed(*, order: Any, actor: Any | None = None,
                         extra: Mapping[str, Any] | None = None) -> None:
    """Order lifecycle completed / closed."""
    emit_event("order.completed", order=order, actor=actor, extra=extra)


def emit_order_reassigned(*, order: Any, actor: Any | None = None,
                          extra: Mapping[str, Any] | None = None) -> None:
    """Order reassigned to a different writer."""
    emit_event("order.reassigned", order=order, actor=actor, extra=extra)


def emit_order_expired(*, order: Any, actor: Any | None = None,
                       extra: Mapping[str, Any] | None = None) -> None:
    """Order expired (deadline missed / SLA)."""
    emit_event("order.expired", order=order, actor=actor, extra=extra)


def emit_order_assigned(*, order: Any, actor: Any | None = None,
                        extra: Mapping[str, Any] | None = None) -> None:
    """Order assigned to a writer (initial assignment)."""
    emit_event("order.assigned", order=order, actor=actor, extra=extra)


__all__ = [
    "emit_event",
    "emit_order_unpaid",
    "emit_order_paid",
    "emit_order_available",
    "emit_order_in_progress",
    "emit_order_on_hold",
    "emit_order_submitted",
    "emit_order_reviewed",
    "emit_order_revision_requested",
    "emit_order_revision_in_progress",
    "emit_order_revised",
    "emit_order_returned",
    "emit_order_rated",
    "emit_order_approved",
    "emit_order_refunded",
    "emit_order_cancelled",
    "emit_order_archived",
    "emit_order_completed",
    "emit_order_reassigned",
    "emit_order_expired",
    "emit_order_assigned",
]
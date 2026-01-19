# orders/notification_handlers.py
from __future__ import annotations

"""
Order notification handlers.

These handlers register lightweight functions (via the project's
notification handler registry) that forward enriched context to the
notification service. They keep business logic out of the registry and
ensure a consistent payload shape for templates (Vue/email/push).

Each handler:
  * builds a rich context with build_order_context(...)
  * shallow-merges any provided payload
  * calls NotificationService.send_notification(...)
"""

from typing import Any, Dict, Optional

from notifications_system.registry.handler_registry import (
    notification_handler,
)
from notifications_system.services.core import NotificationService
from .notification_context import build_order_context


def _merge(a: Optional[Dict[str, Any]], b: Dict[str, Any]) -> Dict[str, Any]:
    """Shallow-merge dictionaries with ``b`` overriding.

    Args:
        a: Existing/partial payload.
        b: Context produced for the event.

    Returns:
        A new dictionary containing keys from both mappings.
    """
    base = dict(a or {})
    base.update(b)
    return base


def _send(
    *,
    user: Any,
    event: str,
    payload: Optional[Dict[str, Any]],
    subject: str,
    preheader: str,
    **kwargs: Any,
) -> None:
    """Common sender used by all handlers.

    Args:
        user: Recipient user instance.
        event: Canonical event key (e.g., ``order.assigned``).
        payload: Optional custom payload to merge.
        subject: Default subject hint for email templates.
        preheader: Optional preheader/preview text.
        **kwargs: Extra args passed by emitters (order/actor/website/...).
    """
    ctx = build_order_context(
        event=event,
        order=kwargs.get("order"),
        actor=kwargs.get("actor"),
        website=kwargs.get("website"),
        viewer_role=kwargs.get("viewer_role"),
        subject=subject,
        preheader=preheader,
    )
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=_merge(payload, ctx),
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@notification_handler("order.created")
def on_order_created(*, user, event, payload=None, **kw) -> None:
    """Client or staff submitted a new order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order created",
        preheader="A new order has been created.",
        **kw,
    )


@notification_handler("order.assigned")
def on_order_assigned(*, user, event, payload=None, **kw) -> None:
    """Order assigned to a writer."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order assigned",
        preheader="You have a new assignment.",
        **kw,
    )


@notification_handler("order.paid")
def on_order_paid(*, user, event, payload=None, **kw) -> None:
    """Client completed payment for an order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Payment received",
        preheader="Payment has been confirmed.",
        **kw,
    )


@notification_handler("order.payment_failed")
def on_order_payment_failed(*, user, event, payload=None, **kw) -> None:
    """Payment attempt failed for an order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Payment failed",
        preheader="A payment attempt did not go through.",
        **kw,
    )


@notification_handler("order.on_hold")
def on_order_on_hold(*, user, event, payload=None, **kw) -> None:
    """Order moved to hold state."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order on hold",
        preheader="The order is temporarily on hold.",
        **kw,
    )


@notification_handler("order.off_hold")
def on_order_off_hold(*, user, event, payload=None, **kw) -> None:
    """Order removed from hold state."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order off hold",
        preheader="The order has resumed.",
        **kw,
    )


@notification_handler("order.in_progress")
def on_order_in_progress(*, user, event, payload=None, **kw) -> None:
    """Order work started (in progress)."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order in progress",
        preheader="Work on the order has started.",
        **kw,
    )


@notification_handler("order.under_editing")
def on_order_under_editing(*, user, event, payload=None, **kw) -> None:
    """Order is currently under editing."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order under editing",
        preheader="The order is being edited.",
        **kw,
    )


@notification_handler("order.submitted")
def on_order_submitted(*, user, event, payload=None, **kw) -> None:
    """Work submitted for client review."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order submitted",
        preheader="Files have been submitted for review.",
        **kw,
    )


@notification_handler("order.file_uploaded")
def on_order_file_uploaded(*, user, event, payload=None, **kw) -> None:
    """A file was uploaded to the order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="New file uploaded",
        preheader="A new file is available on the order.",
        **kw,
    )


@notification_handler("order.updated")
def on_order_updated(*, user, event, payload=None, **kw) -> None:
    """Order metadata updated."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order updated",
        preheader="Order details were updated.",
        **kw,
    )


@notification_handler("order.revision_requested")
def on_order_revision_requested(*, user, event, payload=None, **kw) -> None:
    """Client requested a revision."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Revision requested",
        preheader="The client requested changes.",
        **kw,
    )


@notification_handler("order.revision_in_progress")
def on_order_revision_in_progress(
    *, user, event, payload=None, **kw
) -> None:
    """Revision work started."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Revision in progress",
        preheader="A revision is underway.",
        **kw,
    )


@notification_handler("order.revised")
def on_order_revision_completed(*, user, event, payload=None, **kw) -> None:
    """Revision submitted for review."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Revision completed",
        preheader="Revised files are ready.",
        **kw,
    )


@notification_handler("order.approved")
def on_order_approved(*, user, event, payload=None, **kw) -> None:
    """Client approved the order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order approved",
        preheader="The order was approved.",
        **kw,
    )


@notification_handler("order.rated")
def on_order_rated(*, user, event, payload=None, **kw) -> None:
    """Client rated the order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order rated",
        preheader="A rating was posted.",
        **kw,
    )


@notification_handler("order.completed")
def on_order_completed(*, user, event, payload=None, **kw) -> None:
    """Order marked as completed (terminal state)."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order completed",
        preheader="This order is complete.",
        **kw,
    )


@notification_handler("order.closed")
def on_order_closed(*, user, event, payload=None, **kw) -> None:
    """Order closed by staff or policy."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order closed",
        preheader="The order has been closed.",
        **kw,
    )


@notification_handler("order.cancellation_requested")
def on_order_cxl_requested(*, user, event, payload=None, **kw) -> None:
    """Client requested cancellation."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Cancellation requested",
        preheader="The client requested cancellation.",
        **kw,
    )


@notification_handler("order.cancelled")
def on_order_cancelled(*, user, event, payload=None, **kw) -> None:
    """Order was cancelled."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order cancelled",
        preheader="The order has been cancelled.",
        **kw,
    )


@notification_handler("order.refunded")
def on_order_refunded(*, user, event, payload=None, **kw) -> None:
    """Order payment refunded."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order refunded",
        preheader="A refund has been issued.",
        **kw,
    )


@notification_handler("order.archived")
def on_order_archived(*, user, event, payload=None, **kw) -> None:
    """Order archived."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order archived",
        preheader="The order was archived.",
        **kw,
    )


@notification_handler("order.unarchived")
def on_order_unarchived(*, user, event, payload=None, **kw) -> None:
    """Order unarchived (restored)."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order restored",
        preheader="The order was restored from archive.",
        **kw,
    )


@notification_handler("order.restored")
def on_order_restored(*, user, event, payload=None, **kw) -> None:
    """Explicit restore transition (if used separately)."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order restored",
        preheader="The order was restored.",
        **kw,
    )


@notification_handler("order.returned")
def on_order_returned_to_progress(
    *, user, event, payload=None, **kw
) -> None:
    """Order moved back to progress state."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order resumed",
        preheader="The order returned to progress.",
        **kw,
    )

@notification_handler("order.preferred_writer_assigned")
def on_order_preferred_writer_assigned(
    *, user, event, payload = None, **kw
) -> None:
    """Order assigned to a writer preferred by the client"""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order Assigned to Your Preferred Writer",
        preheader="The order has been assigned to your preferred writer.",
        **kw
    )


@notification_handler("order.preferred_writer_accepted")
def on_order_preferred_writer_accepted(*, user, event, payload=None, **kw) -> None:
    """Preferred writer accepted the order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Preferred writer accepted",
        preheader="Your preferred writer accepted the order.",
        **kw,
    )


@notification_handler("order.preferred_writer_rejected")
def on_order_preferred_writer_rejected(*, user, event, payload=None, **kw) -> None:
    """Preferred writer rejected the order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Preferred writer rejected",
        preheader="Your preferred writer declined the order.",
        **kw,
    )


@notification_handler("order.assignment_accepted")
def on_order_assignment_accepted(*, user, event, payload=None, **kw) -> None:
    """Writer accepted assignment."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Assignment accepted",
        preheader="A writer accepted the assignment.",
        **kw,
    )


@notification_handler("order.assignment_rejected")
def on_order_assignment_rejected(*, user, event, payload=None, **kw) -> None:
    """Writer rejected assignment."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Assignment rejected",
        preheader="A writer rejected the assignment.",
        **kw,
    )


@notification_handler("order.reassigned")
def on_order_reassigned(*, user, event, payload=None, **kw) -> None:
    """Order reassigned to a different writer."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order reassigned",
        preheader="The order has been reassigned.",
        **kw,
    )


@notification_handler("order.unassigned")
def on_order_unassigned(*, user, event, payload=None, **kw) -> None:
    """Writer unassigned from the order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Writer unassigned",
        preheader="The writer was removed from the order.",
        **kw,
    )


@notification_handler("order.fined")
def on_order_fined(*, user, event, payload=None, **kw) -> None:
    """Fine applied to an order."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Fine applied",
        preheader="A fine was applied for this order.",
        **kw,
    )


@notification_handler("order.disputed")
def on_order_disputed(*, user, event, payload=None, **kw) -> None:
    """Order disputed."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Order disputed",
        preheader="The order is under dispute.",
        **kw,
    )
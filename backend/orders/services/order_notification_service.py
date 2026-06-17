from __future__ import annotations

import logging
from typing import Any, Optional

from notifications_system.services.notification_service import NotificationService

log = logging.getLogger(__name__)


class OrderNotificationService:
    """
    Notification boundary for order lifecycle events.
    """

    @classmethod
    def _base_context(cls, order) -> dict:
        return {
            "order_id": order.pk,
            "order_topic": (getattr(order, "topic", None) or "")[:80],
            "order_reference": getattr(order, "reference", str(order.pk)),
            "order_status": order.status,
        }

    @classmethod
    def _notify(
        cls,
        *,
        event_key: str,
        order,
        recipient,
        actor=None,
        context: dict | None = None,
        priority: str = "normal",
        is_critical: bool = False,
    ) -> None:
        if recipient is None:
            return
        try:
            NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=order.website,
                context={**cls._base_context(order), **(context or {})},
                triggered_by=actor,
                priority=priority,
                is_critical=is_critical,
            )
        except Exception as exc:
            log.exception(
                "Order notification failed event=%s order=%s: %s",
                event_key,
                order.pk,
                exc,
            )

    @classmethod
    def notify_order_assigned(
        cls, *, order, writer_user, triggered_by=None
    ) -> None:
        ctx = {"writer_id": getattr(writer_user, "pk", None)}
        cls._notify(
            event_key="order.assigned",
            order=order,
            recipient=writer_user,
            actor=triggered_by,
            context=ctx,
        )
        if order.client:
            cls._notify(
                event_key="order.assigned",
                order=order,
                recipient=order.client,
                actor=triggered_by,
                context=ctx,
            )

    @classmethod
    def notify_order_submitted(cls, *, order, submitted_by) -> None:
        if order.client:
            cls._notify(
                event_key="order.submitted",
                order=order,
                recipient=order.client,
                actor=submitted_by,
            )

    @classmethod
    def notify_order_approved(cls, *, order, approved_by) -> None:
        writer_user = cls._resolve_writer_user(order)
        cls._notify(
            event_key="order.approved",
            order=order,
            recipient=writer_user,
            actor=approved_by,
        )

    @classmethod
    def notify_order_completed(cls, *, order, completed_by) -> None:
        writer_user = cls._resolve_writer_user(order)
        if writer_user:
            cls._notify(
                event_key="order.completed",
                order=order,
                recipient=writer_user,
                actor=completed_by,
            )
        if order.client:
            cls._notify(
                event_key="order.completed",
                order=order,
                recipient=order.client,
                actor=completed_by,
            )

    @classmethod
    def notify_order_cancelled(
        cls, *, order, cancelled_by, reason: str = ""
    ) -> None:
        ctx = {"reason": reason}
        if order.client:
            cls._notify(
                event_key="order.cancelled",
                order=order,
                recipient=order.client,
                actor=cancelled_by,
                context=ctx,
            )
        writer_user = cls._resolve_writer_user(order)
        if writer_user:
            cls._notify(
                event_key="order.cancelled",
                order=order,
                recipient=writer_user,
                actor=cancelled_by,
                context=ctx,
            )

    @classmethod
    def notify_order_revision_requested(
        cls, *, order, requested_by, reason: str = ""
    ) -> None:
        writer_user = cls._resolve_writer_user(order)
        cls._notify(
            event_key="order.revision_requested",
            order=order,
            recipient=writer_user,
            actor=requested_by,
            context={"reason": reason},
        )

    @classmethod
    def notify_order_on_hold(
        cls, *, order, hold, triggered_by=None
    ) -> None:
        ctx = {
            "hold_id": getattr(hold, "pk", None),
            "reason": getattr(hold, "reason", ""),
        }
        writer_user = cls._resolve_writer_user(order)
        if writer_user:
            cls._notify(
                event_key="order.on_hold",
                order=order,
                recipient=writer_user,
                actor=triggered_by,
                context=ctx,
            )
        if order.client:
            cls._notify(
                event_key="order.on_hold",
                order=order,
                recipient=order.client,
                actor=triggered_by,
                context=ctx,
            )

    @classmethod
    def notify_order_reopened(
        cls, *, order, reopened_by, reason: str = ""
    ) -> None:
        ctx = {"reason": reason}
        writer_user = cls._resolve_writer_user(order)
        if writer_user:
            cls._notify(
                event_key="order.reopened",
                order=order,
                recipient=writer_user,
                actor=reopened_by,
                context=ctx,
            )
        if order.client:
            cls._notify(
                event_key="order.reopened",
                order=order,
                recipient=order.client,
                actor=reopened_by,
                context=ctx,
            )

    @classmethod
    def notify_bid_placed(cls, *, interest) -> None:
        cls._notify(
            event_key="order.bid.placed",
            order=interest.order,
            recipient=interest.writer,
            context={"interest_id": interest.pk},
        )

    @classmethod
    def notify_bid_accepted(cls, *, interest, triggered_by=None) -> None:
        cls._notify(
            event_key="order.bid.accepted",
            order=interest.order,
            recipient=interest.writer,
            actor=triggered_by,
            context={"interest_id": interest.pk},
        )

    @classmethod
    def notify_bid_rejected(cls, *, interest, triggered_by=None) -> None:
        cls._notify(
            event_key="order.bid.rejected",
            order=interest.order,
            recipient=interest.writer,
            actor=triggered_by,
            context={"interest_id": interest.pk},
        )

    @classmethod
    def notify_bid_reactivated(cls, *, interest) -> None:
        cls._notify(
            event_key="order.bid.reactivated",
            order=interest.order,
            recipient=interest.writer,
            context={"interest_id": interest.pk},
        )

    @classmethod
    def notify_file_uploaded(
        cls, *, order, uploaded_by, attachment, recipient
    ) -> None:
        cls._notify(
            event_key="file.uploaded",
            order=order,
            recipient=recipient,
            actor=uploaded_by,
            context={
                "attachment_id": getattr(attachment, "pk", None),
                "purpose": getattr(attachment, "purpose", ""),
            },
        )

    @classmethod
    def _adjustment_context(cls, adjustment_request) -> dict:
        return {
            "adjustment_request_id": adjustment_request.pk,
            "adjustment_kind": adjustment_request.adjustment_kind,
            "adjustment_type": adjustment_request.adjustment_type,
            "adjustment_status": adjustment_request.status,
            "adjustment_title": adjustment_request.title,
            "unit_type": adjustment_request.unit_type,
            "requested_quantity": adjustment_request.requested_quantity,
            "countered_quantity": adjustment_request.countered_quantity,
        }

    @classmethod
    def _notify_staff_for_adjustment(
        cls,
        *,
        adjustment_request,
        event_key: str,
        actor=None,
        priority: str = "normal",
    ) -> None:
        try:
            NotificationService.notify_staff(
                event_key=event_key,
                website=adjustment_request.website,
                context={
                    **cls._base_context(adjustment_request.order),
                    **cls._adjustment_context(adjustment_request),
                },
                triggered_by=actor,
                priority=priority,
            )
        except Exception as exc:
            log.exception(
                "Order adjustment staff notification failed event=%s adjustment=%s: %s",
                event_key,
                adjustment_request.pk,
                exc,
            )

    @classmethod
    def notify_adjustment_created(cls, *, adjustment_request, created_by) -> None:
        order = adjustment_request.order
        if order.client:
            cls._notify(
                event_key="order.adjustment.created",
                order=order,
                recipient=order.client,
                actor=created_by,
                context=cls._adjustment_context(adjustment_request),
                priority="high",
            )
        cls._notify_staff_for_adjustment(
            adjustment_request=adjustment_request,
            event_key="order.adjustment.created",
            actor=created_by,
            priority="high",
        )

    @classmethod
    def notify_adjustment_countered(cls, *, adjustment_request, countered_by) -> None:
        writer_user = cls._resolve_writer_user(adjustment_request.order)
        cls._notify(
            event_key="order.adjustment.countered",
            order=adjustment_request.order,
            recipient=writer_user,
            actor=countered_by,
            context=cls._adjustment_context(adjustment_request),
            priority="high",
        )

    @classmethod
    def notify_adjustment_accepted(cls, *, adjustment_request, accepted_by) -> None:
        writer_user = cls._resolve_writer_user(adjustment_request.order)
        cls._notify(
            event_key="order.adjustment.accepted",
            order=adjustment_request.order,
            recipient=writer_user,
            actor=accepted_by,
            context=cls._adjustment_context(adjustment_request),
            priority="high",
        )

    @classmethod
    def notify_adjustment_declined(cls, *, adjustment_request, declined_by) -> None:
        writer_user = cls._resolve_writer_user(adjustment_request.order)
        cls._notify(
            event_key="order.adjustment.declined",
            order=adjustment_request.order,
            recipient=writer_user,
            actor=declined_by,
            context=cls._adjustment_context(adjustment_request),
            priority="high",
        )

    @classmethod
    def notify_adjustment_cancelled(cls, *, adjustment_request, cancelled_by) -> None:
        order = adjustment_request.order
        if order.client:
            cls._notify(
                event_key="order.adjustment.cancelled",
                order=order,
                recipient=order.client,
                actor=cancelled_by,
                context=cls._adjustment_context(adjustment_request),
            )
        writer_user = cls._resolve_writer_user(order)
        cls._notify(
            event_key="order.adjustment.cancelled",
            order=order,
            recipient=writer_user,
            actor=cancelled_by,
            context=cls._adjustment_context(adjustment_request),
        )

    @classmethod
    def notify_adjustment_escalated(cls, *, adjustment_request, escalated_by) -> None:
        cls._notify_staff_for_adjustment(
            adjustment_request=adjustment_request,
            event_key="order.adjustment.escalated",
            actor=escalated_by,
            priority="high",
        )

    @classmethod
    def notify_adjustment_escalation_resolved(
        cls, *, adjustment_request, resolved_by
    ) -> None:
        writer_user = cls._resolve_writer_user(adjustment_request.order)
        cls._notify(
            event_key="order.adjustment.escalation_resolved",
            order=adjustment_request.order,
            recipient=writer_user,
            actor=resolved_by,
            context=cls._adjustment_context(adjustment_request),
        )

    @classmethod
    def notify_order_deadline_approaching(
        cls, *, order, hours_remaining: int
    ) -> None:
        writer_user = cls._resolve_writer_user(order)
        cls._notify(
            event_key="order.deadline_approaching",
            order=order,
            recipient=writer_user,
            context={"hours_remaining": hours_remaining},
            priority="high",
        )

    @staticmethod
    def _resolve_writer_user(order) -> Optional[Any]:
        try:
            return order.assigned_writer
        except Exception:
            return None

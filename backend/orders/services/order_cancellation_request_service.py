from __future__ import annotations

from typing import Any, Optional
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders.constants import (
    ORDER_TIMELINE_EVENT_CANCELLATION_APPROVED,
    ORDER_TIMELINE_EVENT_CANCELLATION_REJECTED,
    ORDER_TIMELINE_EVENT_CANCELLATION_REQUESTED,
)
from orders.models.orders.enums import OrderStatus
from orders.models.orders.order_cancellation_request import OrderCancellationRequest
from orders.models.orders.order_timeline_event import OrderTimelineEvent
from orders.services.order_forfeiture_calculator_service import (
    OrderForfeitureCalculatorService,
)


_CLIENT_REQUESTABLE_STATUSES = frozenset({
    OrderStatus.IN_PROGRESS,
    OrderStatus.READY_FOR_STAFFING,
    OrderStatus.ON_HOLD,
    OrderStatus.PENDING_WRITER_ACCEPTANCE,
})


class OrderCancellationRequestService:
    """
    Two-step cancellation workflow:

    1. client calls request_cancellation  → order → pending_cancellation
    2. staff calls approve or reject
       - approve: delegates to OrderCancellationService.cancel_order
       - reject:  reverts order to pre-request status
    """

    @classmethod
    @transaction.atomic
    def request_cancellation(
        cls,
        *,
        order,
        requested_by: Any,
        reason: str,
    ) -> OrderCancellationRequest:
        if order.status.value not in {s.value for s in _CLIENT_REQUESTABLE_STATUSES}:
            raise ValidationError(
                f"Cannot request cancellation from status '{order.status}'."
            )

        if OrderCancellationRequest.objects.filter(
            order=order,
            status=OrderCancellationRequest.STATUS_PENDING,
        ).exists():
            raise ValidationError(
                "A cancellation request is already pending for this order."
            )

        forfeiture_pct, forfeiture_amount, refund_amount = (
            OrderForfeitureCalculatorService.calculate(order=order)
        )

        pre_status = order.status.value if hasattr(order.status, "value") else order.status

        req = OrderCancellationRequest.objects.create(
            website=order.website,
            order=order,
            requested_by=requested_by,
            reason=reason,
            pre_request_status=pre_status,
            forfeiture_pct=forfeiture_pct,
            forfeiture_amount=forfeiture_amount,
            refund_amount=refund_amount,
        )

        order.status = OrderStatus.PENDING_CANCELLATION
        order.save(update_fields=["status", "updated_at"])

        OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=ORDER_TIMELINE_EVENT_CANCELLATION_REQUESTED,
            actor=requested_by,
            metadata={
                "cancellation_request_id": req.pk,
                "reason": reason,
                "forfeiture_pct": str(forfeiture_pct),
                "forfeiture_amount": str(forfeiture_amount),
                "refund_amount": str(refund_amount),
            },
        )

        cls._notify_staff_cancellation_requested(req=req)
        return req

    @classmethod
    @transaction.atomic
    def approve_cancellation(
        cls,
        *,
        cancellation_request: OrderCancellationRequest,
        reviewed_by: Any,
        refund_destination: str,
        forfeiture_pct_override: Optional[Decimal] = None,
        notes: str = "",
    ) -> OrderCancellationRequest:
        if cancellation_request.status != OrderCancellationRequest.STATUS_PENDING:
            raise ValidationError(
                f"Cannot approve: request is already {cancellation_request.status}."
            )

        if forfeiture_pct_override is not None:
            pct = Decimal(str(forfeiture_pct_override)).quantize(Decimal("0.01"))
            if not (Decimal("0") <= pct <= Decimal("80")):
                raise ValidationError("forfeiture_pct must be between 0 and 80.")
            paid = OrderForfeitureCalculatorService._paid(cancellation_request.order)
            forfeiture_amount = (pct / Decimal("100") * paid).quantize(Decimal("0.01"))
            refund_amount = (paid - forfeiture_amount).quantize(Decimal("0.01"))
            cancellation_request.forfeiture_pct = pct
            cancellation_request.forfeiture_amount = forfeiture_amount
            cancellation_request.refund_amount = refund_amount

        cancellation_request.status = OrderCancellationRequest.STATUS_APPROVED
        cancellation_request.reviewed_by = reviewed_by
        cancellation_request.reviewed_at = timezone.now()
        cancellation_request.reviewer_notes = notes
        cancellation_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "reviewer_notes",
                "forfeiture_pct",
                "forfeiture_amount",
                "refund_amount",
            ]
        )

        from orders.services.order_cancellation_service import OrderCancellationService

        OrderCancellationService.cancel_order(
            order=cancellation_request.order,
            cancelled_by=reviewed_by,
            reason=cancellation_request.reason,
            refund_destination=refund_destination,
            triggered_by=cancellation_request.requested_by,
            notes=notes,
        )

        OrderTimelineEvent.objects.create(
            website=cancellation_request.order.website,
            order=cancellation_request.order,
            event_type=ORDER_TIMELINE_EVENT_CANCELLATION_APPROVED,
            actor=reviewed_by,
            metadata={
                "cancellation_request_id": cancellation_request.pk,
                "forfeiture_pct": str(cancellation_request.forfeiture_pct),
                "refund_amount": str(cancellation_request.refund_amount),
                "notes": notes,
            },
        )
        return cancellation_request

    @classmethod
    @transaction.atomic
    def reject_cancellation(
        cls,
        *,
        cancellation_request: OrderCancellationRequest,
        reviewed_by: Any,
        notes: str = "",
    ) -> OrderCancellationRequest:
        if cancellation_request.status != OrderCancellationRequest.STATUS_PENDING:
            raise ValidationError(
                f"Cannot reject: request is already {cancellation_request.status}."
            )

        cancellation_request.status = OrderCancellationRequest.STATUS_REJECTED
        cancellation_request.reviewed_by = reviewed_by
        cancellation_request.reviewed_at = timezone.now()
        cancellation_request.reviewer_notes = notes
        cancellation_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "reviewer_notes",
            ]
        )

        order = cancellation_request.order
        order.status = cancellation_request.pre_request_status
        order.save(update_fields=["status", "updated_at"])

        OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=ORDER_TIMELINE_EVENT_CANCELLATION_REJECTED,
            actor=reviewed_by,
            metadata={
                "cancellation_request_id": cancellation_request.pk,
                "reverted_to_status": cancellation_request.pre_request_status,
                "notes": notes,
            },
        )

        cls._notify_client_cancellation_rejected(
            req=cancellation_request, notes=notes
        )
        return cancellation_request

    @staticmethod
    def _notify_staff_cancellation_requested(
        *, req: OrderCancellationRequest
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify(
                event_key="order.cancellation_requested",
                recipient=None,
                website=req.website,
                context={
                    "order_id": req.order_id,
                    "requested_by_id": req.requested_by_id,
                    "reason": req.reason,
                    "forfeiture_pct": str(req.forfeiture_pct),
                },
                channels={"in_app": True, "email": False},
                triggered_by=req.requested_by,
                priority="high",
                is_broadcast=True,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception:
            import logging
            logging.getLogger(__name__).warning(
                "Failed to notify staff of cancellation request %s", req.pk,
                exc_info=True,
            )

    @staticmethod
    def _notify_client_cancellation_rejected(
        *, req: OrderCancellationRequest, notes: str
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify(
                event_key="order.cancellation_rejected",
                recipient=req.requested_by,
                website=req.website,
                context={
                    "order_id": req.order_id,
                    "notes": notes,
                },
                channels={"in_app": True, "email": True},
                triggered_by=req.reviewed_by,
                priority="normal",
                is_broadcast=False,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception:
            import logging
            logging.getLogger(__name__).warning(
                "Failed to notify client of cancellation rejection %s", req.pk,
                exc_info=True,
            )

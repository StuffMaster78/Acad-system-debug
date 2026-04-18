from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.constants import (
    UnpaidOrderDispatchStatus,
)
from orders.selectors.unpaid_order_dispatch_selectors import (
    UnpaidOrderMessageDispatchSelector,
)
from orders.services.unpaid_order_message_service import (
    UnpaidOrderMessageService,
)


class UnpaidOrderMessageDispatchService:
    """
    Executes, cancels, and maintains unpaid order reminder dispatches.
    """

    @staticmethod
    @transaction.atomic
    def cancel_pending_dispatches_for_order(*, order) -> int:
        """
        Mark pending dispatches as cancelled for an order.
        """
        now = timezone.now()
        pending_dispatches = (
            UnpaidOrderMessageDispatchSelector.get_pending_dispatches_for_order(
                order=order,
            )
        )

        return pending_dispatches.update(
            status=UnpaidOrderDispatchStatus.CANCELLED,
            cancelled_at=now,
            error_message=(
                "Dispatch cancelled because order became ineligible."
            ),
        )

    @staticmethod
    @transaction.atomic
    def send_dispatch(*, dispatch) -> bool:
        """
        Send a single pending unpaid order reminder dispatch.
        """
        if dispatch.status != UnpaidOrderDispatchStatus.PENDING:
            return False

        dispatch.attempted_at = timezone.now()

        order = dispatch.order
        if not UnpaidOrderMessageService.order_is_eligible(order=order):
            dispatch.status = UnpaidOrderDispatchStatus.SKIPPED
            dispatch.error_message = (
                "Dispatch skipped because order is no longer eligible."
            )
            dispatch.failed_at = timezone.now()
            dispatch.save(
                update_fields=[
                    "attempted_at",
                    "status",
                    "error_message",
                    "failed_at",
                ],
            )
            return False

        try:
            NotificationService.notify(
                event_key="orders.unpaid_order_reminder",
                recipient=dispatch.client,
                website=dispatch.website,
                context={
                    "order_id": order.pk,
                    "topic": getattr(order, "topic", ""),
                    "amount": getattr(order, "total_price", ""),
                    "message": dispatch.message_snapshot,
                    "subject": dispatch.subject_snapshot,
                    "payment_link": f"/orders/{order.pk}/pay",
                },
                channels=["email", "in_app"],
                triggered_by=None,
                priority="normal",
                is_critical=False,
                is_silent=False,
                is_digest=False,
                is_broadcast=False,
                digest_group=None,
            )
        except Exception as exc:
            dispatch.status = UnpaidOrderDispatchStatus.FAILED
            dispatch.failed_at = timezone.now()
            dispatch.error_message = str(exc)
            dispatch.save(
                update_fields=[
                    "attempted_at",
                    "status",
                    "failed_at",
                    "error_message",
                ],
            )
            return False

        dispatch.status = UnpaidOrderDispatchStatus.SENT
        dispatch.sent_at = timezone.now()
        dispatch.error_message = ""
        dispatch.save(
            update_fields=[
                "attempted_at",
                "status",
                "sent_at",
                "error_message",
            ],
        )

        if dispatch.unpaid_order_message.cancel_order_after_send:
            UnpaidOrderMessageDispatchService.cancel_order_for_unpaid_timeout(
                order=order,
            )

        return True

    @staticmethod
    @transaction.atomic
    def cancel_order_for_unpaid_timeout(*, order) -> None:
        """
        Cancel an unpaid order after the final reminder if still eligible.
        """
        if not UnpaidOrderMessageService.order_is_eligible(order=order):
            return

        order.status = "cancelled"
        if hasattr(order, "cancellation_reason"):
            order.cancellation_reason = "unpaid_timeout"
        if hasattr(order, "cancelled_by_system"):
            order.cancelled_by_system = True
        if hasattr(order, "cancelled_at"):
            order.cancelled_at = timezone.now()

        update_fields = ["status"]
        for field_name in (
            "cancellation_reason",
            "cancelled_by_system",
            "cancelled_at",
        ):
            if hasattr(order, field_name):
                update_fields.append(field_name)

        order.save(update_fields=update_fields)

        UnpaidOrderMessageDispatchService.cancel_pending_dispatches_for_order(
            order=order,
        )

    @staticmethod
    def process_due_dispatches(*, website=None) -> int:
        """
        Process all due pending dispatches.

        Returns the count of successful sends.
        """
        dispatches = (
            UnpaidOrderMessageDispatchSelector.get_due_pending_dispatches(
                website=website,
            )
        )

        sent_count = 0
        for dispatch in dispatches:
            if UnpaidOrderMessageDispatchService.send_dispatch(
                dispatch=dispatch,
            ):
                sent_count += 1

        return sent_count
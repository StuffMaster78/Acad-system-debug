from __future__ import annotations

from typing import Any

from notifications_system.services.notification_service import (
    NotificationService,
)


class SpecialOrderNotificationService:
    """
    Central notification wrapper for special order events.
    """

    @staticmethod
    def notify(
        *,
        event_key: str,
        special_order,
        recipient,
        triggered_by=None,
        context: dict[str, Any] | None = None,
        priority: str = "normal",
    ):
        """
        Send a tenant-aware special order notification.
        """
        payload = {
            "special_order_id": special_order.id,
            "title": special_order.title,
            "status": special_order.status,
            **(context or {}),
        }

        return NotificationService.notify(
            event_key=event_key,
            recipient=recipient,
            website=special_order.website,
            context=payload,
            triggered_by=triggered_by,
            priority=priority,
        )

    @classmethod
    def quote_sent(cls, *, quote, triggered_by=None) -> None:
        cls.notify(
            event_key="special_order.quote.sent",
            special_order=quote.special_order,
            recipient=quote.special_order.client,
            triggered_by=triggered_by,
            context={
                "quote_id": quote.id,
                "total_amount": str(quote.total_amount),
                "currency": quote.currency,
                "expires_at": (
                    quote.expires_at.isoformat()
                    if quote.expires_at
                    else None
                ),
            },
        )

    @classmethod
    def quote_accepted(cls, *, quote, triggered_by=None) -> None:
        cls.notify(
            event_key="special_order.quote.accepted",
            special_order=quote.special_order,
            recipient=triggered_by or quote.special_order.client,
            triggered_by=triggered_by,
            context={
                "quote_id": quote.id,
                "total_amount": str(quote.total_amount),
            },
        )

    @classmethod
    def payment_applied(cls, *, payment_application, triggered_by=None) -> None:
        cls.notify(
            event_key="special_order.payment.applied",
            special_order=payment_application.special_order,
            recipient=payment_application.special_order.client,
            triggered_by=triggered_by,
            context={
                "payment_application_id": payment_application.id,
                "amount": str(payment_application.amount),
                "source": payment_application.source,
                "currency": payment_application.currency,
            },
        )

    @classmethod
    def refund_applied(cls, *, refund_application, triggered_by=None) -> None:
        cls.notify(
            event_key="special_order.refund.applied",
            special_order=refund_application.special_order,
            recipient=refund_application.special_order.client,
            triggered_by=triggered_by,
            context={
                "refund_application_id": refund_application.id,
                "amount": str(refund_application.amount),
                "destination": refund_application.destination,
            },
        )
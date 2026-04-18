from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from orders.selectors.unpaid_order_message_selectors import (
    UnpaidOrderMessageSelector,
)
from orders.services.unpaid_order_order_status_service import (
    UnpaidOrderStatusService,
)


class UnpaidOrderMessageService:
    """
    Orchestrates scheduling of unpaid order reminders.
    """

    @staticmethod
    def order_is_eligible(*, order) -> bool:
        """
        Return True when the order still qualifies for unpaid reminders.
        """
        if getattr(order, "status", None) not in {"pending", "unpaid"}:
            return False

        client = getattr(order, "client", None)
        if client is None or not client.email:
            return False

        snapshot = UnpaidOrderStatusService.get_order_funding_snapshot(
            order=order,
        )
        if snapshot.can_activate_order or snapshot.is_fully_paid:
            return False

        return True

    @staticmethod
    def build_message_context(*, order) -> dict[str, object]:
        """
        Return template context for reminder message rendering.
        """
        return {
            "order_id": order.pk,
            "topic": getattr(order, "topic", ""),
            "amount": getattr(order, "total_price", ""),
            "payment_link": f"/orders/{order.pk}/pay",
        }

    @staticmethod
    def render_template(*, template: str, context: dict[str, object]) -> str:
        """
        Render a lightweight string template using format mapping.
        """
        return template.format(**context)

    @staticmethod
    @transaction.atomic
    def schedule_due_dispatches_for_order(*, order) -> int:
        """
        Create missing pending dispatches for active reminder messages.

        Returns the number of dispatches created.
        """
        if not UnpaidOrderMessageService.order_is_eligible(order=order):
            return 0

        messages = UnpaidOrderMessageSelector.get_active_messages_for_website(
            website=order.website,
        )
        now = timezone.now()
        created_count = 0

        from orders.models.legacy_models.unpaid_order_message_dispatch import (
            UnpaidOrderMessageDispatch,
        )

        context = UnpaidOrderMessageService.build_message_context(order=order)

        for message in messages:
            scheduled_for = order.created_at + timedelta(
                hours=message.interval_hours,
            )
            defaults = {
                "website": order.website,
                "client": order.client,
                "recipient_email": order.client.email,
                "subject_snapshot": (
                    UnpaidOrderMessageService.render_template(
                        template=message.subject,
                        context=context,
                    )
                ),
                "message_snapshot": (
                    UnpaidOrderMessageService.render_template(
                        template=message.message,
                        context=context,
                    )
                ),
                "scheduled_for": scheduled_for,
            }

            _, created = UnpaidOrderMessageDispatch.objects.get_or_create(
                order=order,
                unpaid_order_message=message,
                defaults=defaults,
            )
            if created:
                created_count += 1

        return created_count
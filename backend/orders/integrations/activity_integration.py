from __future__ import annotations

from activity.constants import ActivityAudience
from activity.constants import ActivitySeverity
from activity.constants import ActivityVerb
from activity.services.activity_service import ActivityService


class OrderActivityIntegration:
    """
    Emits activity events for order lifecycle.
    """

    @staticmethod
    def order_created(*, order, actor) -> None:
        ActivityService.record_event(
            website=order.website,
            verb=ActivityVerb.ORDER_CREATED,
            actor=actor,
            target=order,
            audiences=[
                ActivityAudience.STAFF,
                ActivityAudience.CLIENT,
            ],
            severity=ActivitySeverity.INFO,
            title="Order created",
            summary=f"Order #{order.id} created",
            metadata={
                "order_id": str(order.id),
                "price": str(order.price),
            },
        )

    @staticmethod
    def order_assigned(*, order, actor, writer) -> None:
        ActivityService.record_event(
            website=order.website,
            verb=ActivityVerb.ORDER_ASSIGNED,
            actor=actor,
            target=order,
            subject=writer,
            audiences=[ActivityAudience.STAFF],
            severity=ActivitySeverity.INFO,
            title="Order assigned",
            summary=f"Order #{order.id} assigned",
            metadata={
                "writer_id": str(writer.id),
            },
        )

    @staticmethod
    def order_completed(*, order, actor) -> None:
        ActivityService.record_event(
            website=order.website,
            verb=ActivityVerb.ORDER_COMPLETED,
            actor=actor,
            target=order,
            audiences=[
                ActivityAudience.CLIENT,
                ActivityAudience.STAFF,
            ],
            severity=ActivitySeverity.SUCCESS,
            title="Order completed",
            summary=f"Order #{order.id} completed",
        )
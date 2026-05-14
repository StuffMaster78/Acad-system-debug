from uuid import UUID

from users.models.user import User, UserRole
from orders.models import Order
from writer_compensation.services.bonus_service import BonusService
from event_system.models.event_outbox import EventOutbox


class BonusEventConsumer:
    """
    Handles bonus-related events from the event system.
    """

    @staticmethod
    def handle(event: EventOutbox) -> None:
        payload = event.payload
        event_type = event.event_type

        if event_type == "bonus.performance_awarded":
            BonusEventConsumer._performance(payload)

        elif event_type == "bonus.milestone_awarded":
            BonusEventConsumer._milestone(payload)

    @staticmethod
    def _writer(writer_id: str) -> User:
        return User.objects.get(
            pk=UUID(writer_id),
            role=UserRole.WRITER,
        )

    @staticmethod
    def _performance(payload: dict) -> None:
        writer = BonusEventConsumer._writer(payload["writer_id"])
        order = Order.objects.get(pk=UUID(payload["order_id"]))

        BonusService.apply_performance_bonus(
            writer=writer,
            order=order,
            base_amount=payload["amount"],
        )

    @staticmethod
    def _milestone(payload: dict) -> None:
        writer = BonusEventConsumer._writer(payload["writer_id"])

        BonusService.apply_milestone_bonus(
            writer=writer,
            milestone=payload["milestone"],
            amount=payload["amount"],
        )
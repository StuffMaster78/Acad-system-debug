from orders.actions.base import BaseOrderAction
from orders.order_enums import OrderStatus
from orders.services.submit_order_service import SubmitOrderService
from audit_logging.services import log_audit_action


class SubmitOrderAction(BaseOrderAction):
    """
    Action to mark an order as submitted by the writer.
    """

    def execute(self):
        """
        Executes the action to mark an order as submitted.

        Raises:
            ValueError: If order cannot be submitted.
        """
        service = SubmitOrderService()
        order = service.execute(self.order_id, self.user)

        log_audit_action(
            actor=self.user,
            action="SUBMIT_ORDER",
            target="orders.Order",
            target_id=self.order.id,
            metadata={
                "message"  : "Order submitted by writer.",
                "transition": {
                    "from": OrderStatus.IN_PROGRESS.value,
                    "to": OrderStatus.SUBMITTED.value,
                    "triggered_by": self.user.username,
                    "timestamp": order.updated_at.isoformat() if hasattr(order, "updated_at") else None,
                },
                "order_snapshot": {
                    "order_id": order.id,
                    "total_price": float(order.total_price),
                    "writer_id": order.writer_id if hasattr(order, "writer_id") else None,
                    "auto_routed_to": OrderStatus.UNDER_EDITING.value,
                    "deadline": order.deadline.isoformat() if hasattr(order, "deadline") else None,
                },
                "context": "Writer submitted the order, moving workflow to editing phase.",
                "next_steps_hint": "Expect editor review or client download access while under editing.",
                "notes": "Order submitted by writer and queued for editing phase."
            }
        )
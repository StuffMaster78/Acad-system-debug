from audit_logging.adapters.base import BaseAuditAdapter


class OrderAuditAdapter(BaseAuditAdapter):
    """
    Translates ORDER domain events into audit events.
    """

    def get_domain(self) -> str:
        return "order"

    # -------------------------
    # EVENTS
    # -------------------------

    def order_created(self, order_id: str, amount: float):
        return self.emit(
            action="order.created",
            object_type="order",
            object_id=order_id,
            metadata={
                "amount": amount,
            },
        )

    def order_paid(self, order_id: str, amount: float):
        return self.emit(
            action="order.paid",
            object_type="order",
            object_id=order_id,
            metadata={
                "amount": amount,
            },
        )

    def order_cancelled(self, order_id: str, reason: str):
        return self.emit(
            action="order.cancelled",
            object_type="order",
            object_id=order_id,
            metadata={
                "reason": reason,
            },
            is_sensitive=False,
        )
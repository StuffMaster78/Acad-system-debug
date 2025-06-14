from orders.actions.base import BaseOrderAction
from orders.services.archive_order_service import ArchiveOrderService
from audit_logging.services import log_audit_action


class ArchiveOrderAction(BaseOrderAction):
    # action_name = "archive_order_action"
    def execute(self):
        old_status = self.order.status
        service = ArchiveOrderService()
        result = service.archive_order(self.order_id)

        log_audit_action(
            actor=self.user,
            action="ARCHIVE",
            target="orders.Order",
            target_id=self.order_id,
            changes={"status": [old_status, "archived"]},
            metadata={"message": "Order archived."}
        )
        return result
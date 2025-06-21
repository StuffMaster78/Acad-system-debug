from orders.actions.base import BaseOrderAction
from orders.services.archive_order_service import ArchiveOrderService
from audit_logging.services import log_audit_action
from orders.registry.decorator import register_order_action

@register_order_action("archive_order")
class ArchiveOrderAction(BaseOrderAction):
    """
    Action to archive a specific order.
    This is typically used for manual operations, like an admin action.
    """
    # action_name = "archive_order_action"
    def execute(self):
        """
        Execute the archive order action.
        This will change the status of the order to 'archived'.
        """
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
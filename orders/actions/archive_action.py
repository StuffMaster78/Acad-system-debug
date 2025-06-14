from orders.actions.base import BaseOrderAction
from orders.services.archive_service import ArchiveService
from audit_logging.services import log_audit_action


class ArchiveAction(BaseOrderAction):
    # action_name = "archive_order"
    def execute(self):
        # This one looks generic – adapt if you know the model.
        service = ArchiveService()
        result = service.archive(self.order_id)

        log_audit_action(
            actor=self.user,
            action="ARCHIVE",
            target="orders.Order",  # Adjust if needed
            target_id=self.order_id,
            metadata={"message": "Entity archived via general ArchiveAction."}
        )
        return result
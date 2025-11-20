from orders.actions.base import BaseOrderAction
from orders.services.auto_archive_service import AutoArchiveService
from audit_logging.services.audit_log_service import AuditLogService
from orders.registry.decorator import register_order_action
@register_order_action("autorchive")
class AutorchiveAction(BaseOrderAction):
    """
    Action to archive all orders older than a specified cutoff date.
    This is typically used for bulk operations, like a scheduled job.
    """
    def execute(self):
        """
        Execute the auto-archive action.
        This will archive all orders older than the specified cutoff date.
        """
        service = AutoArchiveService()
        result = service.archive_orders_older_than(
            cutoff_date=self.data.get("cutoff_date"),
            website=self.website,
        )

        AuditLogService.log_auto(
            actor=self.user,
            action="ARCHIVE",
            target="orders.Order",
            target_id=None,
            metadata={
                "message": (f"Archived {result['archived_count']}"
                            f" orders older than {result['cutoff']}"
                )
            }
        )
        return result
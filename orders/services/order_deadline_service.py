from django.utils import timezone
from orders.models import Order
from orders.exceptions import OrderInvalidStateException
from audit_logging.services.audit_log_service import AuditLogService


class OrderDeadlineService:
    @staticmethod
    def update_deadline(order: Order, new_deadline, actor, reason=None):
        if new_deadline <= timezone.now():
            raise ValueError("Deadline must be in the future.")

        old_deadline = order.deadline

        if old_deadline == new_deadline:
            return order  # no-op

        order.deadline = new_deadline
        order.save()

        AuditLogService.log_auto(
            order=order,
            field="deadline",
            old_value=old_deadline.isoformat(),
            new_value=new_deadline.isoformat(),
            changed_by=actor,
            reason=reason or "Manual deadline update"
        )

        return order
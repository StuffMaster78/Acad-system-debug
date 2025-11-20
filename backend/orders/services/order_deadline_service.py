from django.utils import timezone
from orders.models import Order
from orders.exceptions import OrderInvalidStateException
from audit_logging.services.audit_log_service import AuditLogService


class OrderDeadlineService:
    @staticmethod
    def update_deadline(order: Order, new_deadline, actor, reason=None):
        if new_deadline <= timezone.now():
            raise ValueError("Deadline must be in the future.")

        old_deadline = getattr(order, "client_deadline", None)

        if old_deadline == new_deadline:
            return order  # no-op

        # Write to canonical field used by the model
        if hasattr(order, "client_deadline"):
            order.client_deadline = new_deadline
        else:
            # Fallback for any legacy models
            setattr(order, "deadline", new_deadline)
        order.save()

        try:
            AuditLogService.log_auto(
                order=order,
                field="deadline",
                old_value=old_deadline.isoformat() if old_deadline else None,
                new_value=new_deadline.isoformat(),
                changed_by=actor,
                reason=reason or "Manual deadline update"
            )
        except Exception:
            # Do not fail the business operation if audit logging fails in tests
            pass

        return order
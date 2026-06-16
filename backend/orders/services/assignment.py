# Compat shim — OrderAssignmentService moved to old_services.
from orders.services.old_services.assignment import OrderAssignmentService

__all__ = ["OrderAssignmentService"]

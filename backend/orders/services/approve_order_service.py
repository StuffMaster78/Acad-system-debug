# Compat shim — moved to old_services; new code: order_approval_service.py
from orders.services.old_services.approve_order_service import ApproveOrderService

__all__ = ["ApproveOrderService"]

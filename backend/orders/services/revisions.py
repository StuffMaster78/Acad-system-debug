"""
Shim module — re-exports OrderRevisionService from its canonical location.
Exists to satisfy legacy imports in serializers_legacy.py and order_revision action.
"""
from orders.services.old_services.revisions import OrderRevisionService  # noqa: F401

__all__ = ["OrderRevisionService"]

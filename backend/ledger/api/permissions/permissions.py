from __future__ import annotations

from core.permissions.base import BasePlatformPermission


class CanViewLedger(BasePlatformPermission):
    """
    Allow internal finance/admin users to view ledger records.

    Ledger data is sensitive financial truth. It should never be exposed
    to client or writer portals.
    """

    message = "You are not allowed to view ledger records."

    required_portal = "internal_admin"
    required_permission = "ledger.view"
    require_tenant = True


class CanReconcileLedger(BasePlatformPermission):
    """
    Allow internal finance/admin users to manage reconciliation records.
    """

    message = "You are not allowed to reconcile ledger records."

    required_portal = "internal_admin"
    required_permission = "ledger.reconcile"
    require_tenant = True
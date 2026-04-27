from __future__ import annotations

from core.permissions.base import BasePlatformPermission


class CanViewOrderOpsDashboard(BasePlatformPermission):
    """
    Restrict operations dashboard visibility to internal users
    with order visibility permission for the resolved tenant.
    """

    message = "You are not allowed to view the order operations dashboard."

    required_portal = "internal_admin"
    required_permission = "orders.view_all"
    require_tenant = True
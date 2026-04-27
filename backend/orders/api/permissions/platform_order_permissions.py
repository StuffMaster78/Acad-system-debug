from __future__ import annotations

from core.permissions.base import BasePlatformPermission


class InternalOrderAccessPermission(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "orders.view_all"
    require_tenant = True


class ClientOrderAccessPermission(BasePlatformPermission):
    required_portal = "client_portal"
    required_permission = "orders.view_own"
    require_tenant = True


class ClientOrderCreatePermission(BasePlatformPermission):
    required_portal = "client_portal"
    required_permission = "orders.create"
    require_tenant = True


class WriterOrderAccessPermission(BasePlatformPermission):
    required_portal = "writer_portal"
    required_permission = "orders.view_own"
    require_tenant = True


class OrderAssignmentPermission(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "orders.assign_writer"
    require_tenant = True


class OrderCancellationPermission(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "orders.cancel_order"
    require_tenant = True


class OrderMessagingPermission(BasePlatformPermission):
    required_permission = "orders.message_users"
    require_tenant = True
from __future__ import annotations

from core.permissions.base import BasePlatformPermission


class CanViewPayments(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "payments.view"
    require_tenant = True


class CanRefundPayment(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "payments.refund"
    require_tenant = True


class CanCreateClientPayment(BasePlatformPermission):
    required_portal = "client_portal"
    required_permission = "payments.create_own"
    require_tenant = True


class CanViewOwnPayments(BasePlatformPermission):
    required_portal = "client_portal"
    required_permission = "payments.view_own"
    require_tenant = True
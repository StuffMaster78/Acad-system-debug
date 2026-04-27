from __future__ import annotations

from core.permissions.base import BasePlatformPermission


class CanViewOwnWallet(BasePlatformPermission):
    """
    Allow a client or writer to view their own wallet
    within the resolved tenant.
    """

    message = "You are not allowed to view this wallet."

    required_permission = "wallets.view_own"
    require_tenant = True


class CanViewWallets(BasePlatformPermission):
    """
    Allow internal finance/admin users to view tenant wallets.
    """

    message = "You are not allowed to view wallets."

    required_portal = "internal_admin"
    required_permission = "wallets.view"
    require_tenant = True


class CanAdjustWallet(BasePlatformPermission):
    """
    Allow internal finance/admin users to credit or debit wallets.
    """

    message = "You are not allowed to adjust wallets."

    required_portal = "internal_admin"
    required_permission = "wallets.adjust"
    require_tenant = True


class CanManageWalletHolds(BasePlatformPermission):
    """
    Allow internal finance/admin users to create, release,
    or capture wallet holds.
    """

    message = "You are not allowed to manage wallet holds."

    required_portal = "internal_admin"
    required_permission = "wallets.manage_holds"
    require_tenant = True


class CanReconcileWallet(BasePlatformPermission):
    """
    Allow internal finance/admin users to reconcile or repair wallets.
    """

    message = "You are not allowed to reconcile wallets."

    required_portal = "internal_admin"
    required_permission = "wallets.reconcile"
    require_tenant = True
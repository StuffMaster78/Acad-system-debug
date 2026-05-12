from writer_compensation.permissions.base import (
    IsFinanceAdmin,
    IsOwnerOrFinanceStaff,
)


class CanViewExposure(IsOwnerOrFinanceStaff):
    """
    View exposure ledgers.
    """


class CanManageExposure(IsFinanceAdmin):
    """
    Manage exposure systems.
    """
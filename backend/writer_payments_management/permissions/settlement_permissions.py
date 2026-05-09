from writer_payments_management.permissions.base import (
    IsFinanceAdmin,
    IsFinanceStaff,
    IsOwnerOrFinanceStaff,
)


class CanViewSettlement(IsOwnerOrFinanceStaff):
    """
    View settlement records.
    """


class CanManageSettlement(IsFinanceAdmin):
    """
    Create/finalize settlements.
    """


class CanRunSettlement(IsFinanceAdmin):
    """
    Execute settlement workflows.
    """

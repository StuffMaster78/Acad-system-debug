from writer_payments_management.permissions.base import (
    IsFinanceAdmin,
    IsFinanceStaff,
)


class CanViewPayouts(IsFinanceStaff):
    """
    View payout information.
    """


class CanExecutePayouts(IsFinanceAdmin):
    """
    Execute payout operations.
    """


class CanReconcilePayouts(IsFinanceAdmin):
    """
    Run reconciliation workflows.
    """

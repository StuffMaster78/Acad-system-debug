class LedgerError(Exception):
    pass


class LedgerPostingError(LedgerError):
    pass


class LedgerHoldError(LedgerError):
    pass


class LedgerReversalError(LedgerError):
    pass
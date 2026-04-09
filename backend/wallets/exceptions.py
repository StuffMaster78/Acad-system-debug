class WalletError(Exception):
    """Base exception for wallet domain errors."""


class WalletNotFoundError(WalletError):
    """Raised when a wallet cannot be found."""


class WalletInactiveError(WalletError):
    """Raised when an operation is attempted on an inactive wallet."""


class InsufficientWalletBalanceError(WalletError):
    """Raised when a debit exceeds the available wallet balance."""


class WalletHoldError(WalletError):
    """Raised when a wallet hold operation fails."""


class WalletEntryError(WalletError):
    """Raised when a wallet entry operation fails."""


class WalletReconciliationError(WalletError):
    """Raised when wallet reconciliation fails."""


class CrossTenantWalletAccessError(WalletError):
    """Raised when cross tenant wallet access is attempted."""
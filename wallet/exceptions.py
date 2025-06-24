# wallets/exceptions.py
class InsufficientWalletBalance(Exception):
    """Raised when a wallet debit exceeds available balance."""
    pass
class WalletTransactionError(Exception):
    """Base exception for wallet transaction errors."""
    pass
class WalletNotFoundError(WalletTransactionError):
    """Raised when a wallet is not found."""
    def __init__(self, message="Wallet not found."):
        self.message = message
        super().__init__(self.message)
class InvalidTransactionTypeError(WalletTransactionError):
    """Raised when an invalid transaction type is specified."""
    def __init__(self, transaction_type, message="Invalid transaction type."):
        self.transaction_type = transaction_type
        self.message = f"{message} Provided type: {transaction_type}"
        super().__init__(self.message)
class TransactionAlreadyExistsError(WalletTransactionError):
    """Raised when a transaction with the same reference already exists."""
    def __init__(self, reference, message="Transaction with this reference already exists."):
        self.reference = reference
        self.message = f"{message} Reference: {reference}"
        super().__init__(self.message)
class WithdrawalRequestError(Exception):
    """Base exception for withdrawal request errors."""
    pass
class WithdrawalRequestNotFoundError(WithdrawalRequestError):
    """Raised when a withdrawal request is not found."""
    def __init__(self, message="Withdrawal request not found."):
        self.message = message
        super().__init__(self.message)
class WithdrawalRequestAlreadyProcessedError(WithdrawalRequestError):
    """Raised when a withdrawal request has already been processed."""
    def __init__(self, message="Withdrawal request has already been processed."):
        self.message = message
        super().__init__(self.message)
class InsufficientWithdrawalBalanceError(WithdrawalRequestError):
    """Raised when a withdrawal request exceeds available wallet balance."""
    def __init__(self, message="Insufficient wallet balance for this withdrawal."):
        self.message = message
        super().__init__(self.message)
class WithdrawalRequestApprovalError(WithdrawalRequestError):
    """Raised when an error occurs during withdrawal request approval."""
    def __init__(self, message="Error approving withdrawal request."):
        self.message = message
        super().__init__(self.message)
class WithdrawalRequestRejectionError(WithdrawalRequestError):
    """Raised when an error occurs during withdrawal request rejection."""
    def __init__(self, message="Error rejecting withdrawal request."):
        self.message = message
        super().__init__(self.message)
class WalletServiceError(Exception):
    """Base exception for wallet service errors."""
    pass
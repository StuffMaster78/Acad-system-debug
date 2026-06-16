# Compat shim — SmartLockoutService renamed to AccountLockoutService.
from authentication.services.account_lockout_service import AccountLockoutService as SmartLockoutService

__all__ = ["SmartLockoutService"]

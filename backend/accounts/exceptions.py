class AccountsError(Exception):
    """Base exception for the accounts app."""


class AccountProfileAlreadyExistsError(AccountsError):
    """Raised when trying to create a duplicate account profile."""


class InvalidAccountStatusTransitionError(AccountsError):
    """Raised when an invalid account status change is attempted"""


class RoleAlreadyAssignedError(AccountsError):
    """Raised when a role is already assigned to an account."""


class RoleNotAssignedError(AccountsError):
    """Raised when a role is not assigned to an account."""


class InactiveRoleDefinitionError(AccountsError):
    """Raised when trying to assign an inactive role definition."""
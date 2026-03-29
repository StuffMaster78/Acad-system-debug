from accounts.constants import SYSTEM_ROLE_KEYS
from accounts.exceptions import (
    InactiveRoleDefinitionError,
    RoleAlreadyAssignedError,
)


class AccountRoleValidator:
    """Validator for account role actions."""

    @staticmethod
    def validate_role_is_active(*, role) -> None:
        """Ensure the role definition is active."""
        if not role.is_active:
            raise InactiveRoleDefinitionError(
                "Cannot assign an inactive role definition."
            )

    @staticmethod
    def validate_role_not_already_active(*, existing_account_role) -> None:
        """Ensure a role is not already actively assigned."""
        if existing_account_role and existing_account_role.is_active:
            raise RoleAlreadyAssignedError(
                "Role is already assigned to this account profile."
            )

    @staticmethod
    def is_system_role(*, role_key: str) -> bool:
        """Return whether a role key is a protected system role."""
        return role_key in SYSTEM_ROLE_KEYS
from accounts.enums import AccountStatus
from accounts.exceptions import InvalidAccountStatusTransitionError


class AccountStatusValidator:
    """Validator for account status transitions."""

    ALLOWED_TRANSITIONS: dict[AccountStatus, set[AccountStatus]] = {
        AccountStatus.PENDING: {
            AccountStatus.ACTIVE,
            AccountStatus.UNDER_REVIEW,
            AccountStatus.DISABLED,
        },
        AccountStatus.UNDER_REVIEW: {
            AccountStatus.ACTIVE,
            AccountStatus.SUSPENDED,
            AccountStatus.DISABLED,
        },
        AccountStatus.ACTIVE: {
            AccountStatus.SUSPENDED,
            AccountStatus.DISABLED,
        },
        AccountStatus.SUSPENDED: {
            AccountStatus.ACTIVE,
            AccountStatus.DISABLED,
        },
        AccountStatus.DISABLED: set(),
    }

    @classmethod
    def validate_transition(
        cls,
        *,
        current_status: AccountStatus,
        new_status: AccountStatus,
    ) -> None:
        """Validate that a status transition is allowed."""
        allowed: set[AccountStatus] = cls.ALLOWED_TRANSITIONS.get(
            current_status,
            set(),
        )

        if new_status not in allowed:
            raise InvalidAccountStatusTransitionError(
                f"Cannot transition from '{current_status.value}' to "
                f"'{new_status.value}'."
            )
from django.core.exceptions import ValidationError

from authentication.selectors.account_deletion_selectors import (
    get_access_blocking_deletion_request,
)


class AccountAccessPolicyService:
    """
    Enforce whether an account may use authentication flows.
    """

    @staticmethod
    def validate_auth_access(
        *,
        user,
        website,
    ) -> None:
        """
        Raise if the account is in a deletion state that blocks auth.
        """
        deletion_request = get_access_blocking_deletion_request(
            user=user,
            website=website,
        )

        if deletion_request is not None:
            raise ValidationError(
                "This account is no longer accessible."
            )
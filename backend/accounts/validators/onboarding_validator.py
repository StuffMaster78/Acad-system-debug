from accounts.enums import OnboardingStatus
from accounts.exceptions import AccountsError


class OnboardingValidator:
    """Validator for onboarding flow operations."""

    @staticmethod
    def validate_session_can_start(*, existing_session) -> None:
        """Prevent duplicate active onboarding sessions."""
        if existing_session and existing_session.status in {
            OnboardingStatus.NOT_STARTED,
            OnboardingStatus.IN_PROGRESS,
        }:
            raise AccountsError(
                "An onboarding session is already active for this user."
            )

    @staticmethod
    def validate_session_can_complete(*, session) -> None:
        """Ensure an onboarding session can be completed."""
        if session.status == OnboardingStatus.COMPLETED:
            raise AccountsError("This onboarding session is already completed.")

        if session.status == OnboardingStatus.EXPIRED:
            raise AccountsError("This onboarding session has already expired.")
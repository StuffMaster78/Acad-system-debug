from accounts.enums import OnboardingStatus
from accounts.models import OnboardingSession


class OnboardingSelector:
    """Read helpers for onboarding sessions."""

    @staticmethod
    def get_active_session(
        *,
        account_profile,
        onboarding_type: str,
    ):
        """Return the active onboarding session for a profile and type."""
        return OnboardingSession.objects.filter(
            account_profile=account_profile,
            onboarding_type=onboarding_type,
            status__in=[
                OnboardingStatus.NOT_STARTED,
                OnboardingStatus.IN_PROGRESS,
            ],
        ).order_by("-started_at").first()

    @staticmethod
    def get_latest_session(
        *,
        account_profile,
        onboarding_type: str,
    ):
        """Return the latest onboarding session for a profile and type."""
        return OnboardingSession.objects.filter(
            account_profile=account_profile,
            onboarding_type=onboarding_type,
        ).order_by("-started_at").first()
from django.db import transaction
from django.utils import timezone

from accounts.constants import ONBOARDING_SESSION_EXPIRY_HOURS
from accounts.enums import OnboardingStatus
from accounts.models import OnboardingSession
from accounts.selectors.onboarding_selector import OnboardingSelector
from accounts.validators.onboarding_validator import OnboardingValidator


class OnboardingService:
    """Base service for onboarding session lifecycle."""

    @staticmethod
    @transaction.atomic
    def start_session(
        *,
        website,
        user,
        account_profile,
        onboarding_type: str,
        target_role=None,
        actor=None,
        metadata: dict | None = None,
    ) -> OnboardingSession:
        """Start a new onboarding session."""
        existing_session = OnboardingSelector.get_active_session(
            account_profile=account_profile,
            onboarding_type=onboarding_type,
        )
        OnboardingValidator.validate_session_can_start(
            existing_session=existing_session,
        )

        expires_at = timezone.now() + timezone.timedelta(
            hours=ONBOARDING_SESSION_EXPIRY_HOURS
        )

        return OnboardingSession.objects.create(
            website=website,
            user=user,
            account_profile=account_profile,
            onboarding_type=onboarding_type,
            target_role=target_role,
            status=OnboardingStatus.IN_PROGRESS,
            expires_at=expires_at,
            created_by=actor,
            metadata=metadata or {},
        )

    @staticmethod
    @transaction.atomic
    def mark_step(
        *,
        session: OnboardingSession,
        last_step: str,
    ) -> OnboardingSession:
        """Update the last successful onboarding step."""
        session.last_step = last_step
        session.save(update_fields=["last_step", "updated_at"])
        return session

    @staticmethod
    @transaction.atomic
    def complete_session(
        *,
        session: OnboardingSession,
    ) -> OnboardingSession:
        """Mark an onboarding session as completed."""
        OnboardingValidator.validate_session_can_complete(session=session)

        session.status = OnboardingStatus.COMPLETED
        session.completed_at = timezone.now()
        session.save(update_fields=["status", "completed_at", "updated_at"])
        return session

    @staticmethod
    @transaction.atomic
    def expire_session(
        *,
        session: OnboardingSession,
    ) -> OnboardingSession:
        """Mark an onboarding session as expired."""
        session.status = OnboardingStatus.EXPIRED
        session.save(update_fields=["status", "updated_at"])
        return session
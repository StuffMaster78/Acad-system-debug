from django.test import TestCase

from accounts.constants import DEFAULT_CLIENT_ROLE
from accounts.enums import (
    AccountAuditEventType,
    OnboardingStatus,
    OnboardingType,
)
from accounts.models import (
    AccountAuditLog,
    AccountProfile,
    AccountRole,
    OnboardingSession,
    RoleDefinition,
)
from accounts.services.client_onboarding_service import (
    ClientOnboardingService,
)
from users.models.user import User
from websites.models.websites import Website


class ClientOnboardingServiceTests(TestCase):
    """Tests for client onboarding workflows."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="client_user",
            email="client@example.com",
            password="password123",
        )
        self.account_profile = AccountProfile.objects.create(
            website=self.website,
            user=self.user,
        )
        self.client_role = RoleDefinition.objects.create(
            website=self.website,
            key=DEFAULT_CLIENT_ROLE,
            name="Client",
            is_system_role=True,
            is_active=True,
        )

    def test_complete_onboarding(self):
        """It should complete client onboarding successfully."""
        updated_profile = ClientOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
        )

        updated_profile.refresh_from_db()

        self.assertEqual(
            updated_profile.onboarding_status,
            OnboardingStatus.COMPLETED,
        )

        self.assertTrue(
            AccountRole.objects.filter(
                account_profile=updated_profile,
                role=self.client_role,
                is_active=True,
            ).exists()
        )

        self.assertTrue(
            OnboardingSession.objects.filter(
                account_profile=updated_profile,
                onboarding_type=OnboardingType.CLIENT,
                status=OnboardingStatus.COMPLETED,
            ).exists()
        )

        self.assertTrue(
            AccountAuditLog.objects.filter(
                account_profile=updated_profile,
                event_type=(
                    AccountAuditEventType.CLIENT_ONBOARDING_COMPLETED
                ),
            ).exists()
        )

    def test_complete_onboarding_creates_completed_session(self):
        """It should create and complete a client onboarding session."""
        ClientOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
        )

        session = OnboardingSession.objects.get(
            account_profile=self.account_profile,
            onboarding_type=OnboardingType.CLIENT,
        )

        self.assertEqual(session.status, OnboardingStatus.COMPLETED)
        self.assertIsNotNone(session.completed_at)

    def test_complete_onboarding_assigns_client_role(self):
        """It should assign the configured client role."""
        ClientOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
        )

        assigned_role = AccountRole.objects.get(
            account_profile=self.account_profile,
            role=self.client_role,
        )

        self.assertTrue(assigned_role.is_active)
        self.assertEqual(assigned_role.website, self.website)
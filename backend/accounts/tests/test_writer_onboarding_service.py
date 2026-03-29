from django.test import TestCase

from accounts.constants import DEFAULT_WRITER_ROLE
from accounts.enums import (
    AccountAuditEventType,
    AccountStatus,
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
from accounts.services.writer_onboarding_service import (
    WriterOnboardingService,
)
from users.models.user import User
from websites.models.websites import Website


class WriterOnboardingServiceTests(TestCase):
    """Tests for writer onboarding workflows."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="writer_user",
            email="writer@example.com",
            password="password123",
        )
        self.account_profile = AccountProfile.objects.create(
            website=self.website,
            user=self.user,
        )
        self.writer_role = RoleDefinition.objects.create(
            website=self.website,
            key=DEFAULT_WRITER_ROLE,
            name="Writer",
            is_system_role=True,
            is_active=True,
        )

    def test_complete_onboarding_requires_review_by_default(self):
        """It should complete writer onboarding and mark review state."""
        updated_profile = WriterOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
        )

        updated_profile.refresh_from_db()

        self.assertEqual(
            updated_profile.onboarding_status,
            OnboardingStatus.COMPLETED,
        )
        self.assertEqual(
            updated_profile.status,
            AccountStatus.UNDER_REVIEW,
        )

        self.assertTrue(
            AccountRole.objects.filter(
                account_profile=updated_profile,
                role=self.writer_role,
                is_active=True,
            ).exists()
        )

        self.assertTrue(
            OnboardingSession.objects.filter(
                account_profile=updated_profile,
                onboarding_type=OnboardingType.WRITER,
                status=OnboardingStatus.COMPLETED,
            ).exists()
        )

        self.assertTrue(
            AccountAuditLog.objects.filter(
                account_profile=updated_profile,
                event_type=(
                    AccountAuditEventType.WRITER_ONBOARDING_COMPLETED
                ),
            ).exists()
        )

    def test_complete_onboarding_can_activate_without_review(self):
        """It should activate the writer when review is not required."""
        updated_profile = WriterOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
            require_review=False,
        )

        updated_profile.refresh_from_db()

        self.assertEqual(
            updated_profile.onboarding_status,
            OnboardingStatus.COMPLETED,
        )
        self.assertEqual(updated_profile.status, AccountStatus.ACTIVE)

    def test_complete_onboarding_assigns_writer_role(self):
        """It should assign the configured writer role."""
        WriterOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
        )

        assigned_role = AccountRole.objects.get(
            account_profile=self.account_profile,
            role=self.writer_role,
        )

        self.assertTrue(assigned_role.is_active)
        self.assertEqual(assigned_role.website, self.website)
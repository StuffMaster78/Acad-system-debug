from django.test import TestCase

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
from accounts.services.staff_onboarding_service import (
    StaffOnboardingService,
)
from users.models.user import User
from websites.models.websites import Website


class StaffOnboardingServiceTests(TestCase):
    """Tests for staff onboarding workflows."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="password123",
        )
        self.account_profile = AccountProfile.objects.create(
            website=self.website,
            user=self.user,
        )
        self.admin_role = RoleDefinition.objects.create(
            website=self.website,
            key="admin",
            name="Admin",
            is_system_role=True,
            is_active=True,
        )
        self.editor_role = RoleDefinition.objects.create(
            website=self.website,
            key="editor",
            name="Editor",
            is_system_role=True,
            is_active=True,
        )

    def test_complete_onboarding_assigns_staff_roles(self):
        """It should assign one or more staff roles."""
        updated_profile = StaffOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
            role_keys=["admin", "editor"],
        )

        updated_profile.refresh_from_db()

        self.assertTrue(
            AccountRole.objects.filter(
                account_profile=updated_profile,
                role=self.admin_role,
                is_active=True,
            ).exists()
        )
        self.assertTrue(
            AccountRole.objects.filter(
                account_profile=updated_profile,
                role=self.editor_role,
                is_active=True,
            ).exists()
        )

    def test_complete_onboarding_marks_profile_completed_and_active(self):
        """It should complete onboarding and activate the account."""
        updated_profile = StaffOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
            role_keys=["admin"],
        )

        updated_profile.refresh_from_db()

        self.assertEqual(
            updated_profile.onboarding_status,
            OnboardingStatus.COMPLETED,
        )
        self.assertEqual(updated_profile.status, AccountStatus.ACTIVE)

    def test_complete_onboarding_creates_completed_staff_session(self):
        """It should create and complete a staff onboarding session."""
        StaffOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
            role_keys=["admin"],
        )

        session = OnboardingSession.objects.get(
            account_profile=self.account_profile,
            onboarding_type=OnboardingType.STAFF,
        )

        self.assertEqual(session.status, OnboardingStatus.COMPLETED)
        self.assertIsNotNone(session.completed_at)

    def test_complete_onboarding_writes_audit_log(self):
        """It should write a staff onboarding audit event."""
        StaffOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
            role_keys=["admin", "editor"],
        )

        self.assertTrue(
            AccountAuditLog.objects.filter(
                account_profile=self.account_profile,
                event_type=(
                    AccountAuditEventType.STAFF_ONBOARDING_COMPLETED
                ),
            ).exists()
        )

    def test_complete_onboarding_stores_role_keys_in_audit_metadata(self):
        """It should record assigned role keys in audit metadata."""
        StaffOnboardingService.complete_onboarding(
            account_profile=self.account_profile,
            role_keys=["admin", "editor"],
        )

        audit_log = AccountAuditLog.objects.filter(
            account_profile=self.account_profile,
            event_type=AccountAuditEventType.STAFF_ONBOARDING_COMPLETED,
        ).latest("created_at")

        self.assertEqual(
            audit_log.metadata["role_keys"],
            ["admin", "editor"],
        )
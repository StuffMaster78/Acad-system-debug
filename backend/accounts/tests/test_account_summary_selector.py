from django.test import TestCase

from accounts.enums import AccountStatus, OnboardingStatus
from accounts.models import AccountProfile, AccountRole, RoleDefinition
from accounts.selectors.account_summary_selector import (
    AccountSummarySelector,
)
from users.models.user import User
from websites.models.websites import Website


class AccountSummarySelectorTests(TestCase):
    """Tests for account summary selector."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="summary_user",
            email="summary@example.com",
            password="password123",
        )
        self.account_profile = AccountProfile.objects.create(
            website=self.website,
            user=self.user,
            status=AccountStatus.ACTIVE,
            onboarding_status=OnboardingStatus.COMPLETED,
            is_primary=True,
            suspension_reason="",
            metadata={"source": "test"},
        )
        self.client_role = RoleDefinition.objects.create(
            website=self.website,
            key="client",
            name="Client",
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

        AccountRole.objects.create(
            website=self.website,
            account_profile=self.account_profile,
            role=self.client_role,
            is_active=True,
        )
        AccountRole.objects.create(
            website=self.website,
            account_profile=self.account_profile,
            role=self.editor_role,
            is_active=True,
        )

    def test_build_summary_returns_expected_structure(self):
        """It should build a structured account summary."""
        summary = AccountSummarySelector.build_summary(
            website=self.website,
            user=self.user,
        )

        self.assertEqual(summary["account_profile_id"], self.account_profile.id)
        self.assertEqual(summary["website_id"], self.website.id)
        self.assertEqual(summary["user_id"], self.user.id)
        self.assertEqual(summary["status"], AccountStatus.ACTIVE)
        self.assertEqual(
            summary["onboarding_status"],
            OnboardingStatus.COMPLETED,
        )
        self.assertTrue(summary["is_primary"])
        self.assertEqual(summary["metadata"], {"source": "test"})

    def test_build_summary_includes_active_roles(self):
        """It should include active roles in the summary."""
        summary = AccountSummarySelector.build_summary(
            website=self.website,
            user=self.user,
        )

        role_keys = {role["key"] for role in summary["roles"]}

        self.assertEqual(role_keys, {"client", "editor"})

    def test_build_summary_includes_role_metadata(self):
        """It should include role details in the summary."""
        summary = AccountSummarySelector.build_summary(
            website=self.website,
            user=self.user,
        )

        first_role = summary["roles"][0]

        self.assertIn("id", first_role)
        self.assertIn("key", first_role)
        self.assertIn("name", first_role)
        self.assertIn("is_system_role", first_role)
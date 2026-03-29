from django.test import TestCase

from accounts.models import AccountProfile, AccountRole, RoleDefinition
from accounts.selectors.account_role_selector import AccountRoleSelector
from users.models.user import User
from websites.models.websites import Website


class AccountRoleSelectorTests(TestCase):
    """Tests for account role read helpers."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="selector_user",
            email="selector@example.com",
            password="password123",
        )
        self.account_profile = AccountProfile.objects.create(
            website=self.website,
            user=self.user,
        )
        self.client_role = RoleDefinition.objects.create(
            website=self.website,
            key="client",
            name="Client",
            is_system_role=True,
            is_active=True,
        )
        self.writer_role = RoleDefinition.objects.create(
            website=self.website,
            key="writer",
            name="Writer",
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
            role=self.writer_role,
            is_active=False,
        )

    def test_get_active_roles_returns_only_active_roles(self):
        """It should return only active role assignments."""
        active_roles = AccountRoleSelector.get_active_roles(
            account_profile=self.account_profile,
        )

        self.assertEqual(active_roles.count(), 1)
        self.assertEqual(active_roles.first().role.key, "client")

    def test_has_role_returns_true_for_active_role(self):
        """It should report true for an active role."""
        self.assertTrue(
            AccountRoleSelector.has_role(
                account_profile=self.account_profile,
                role_key="client",
            )
        )

    def test_has_role_returns_false_for_inactive_role(self):
        """It should report false for an inactive role."""
        self.assertFalse(
            AccountRoleSelector.has_role(
                account_profile=self.account_profile,
                role_key="writer",
            )
        )

    def test_has_role_returns_false_for_missing_role(self):
        """It should report false when the role is not assigned."""
        self.assertFalse(
            AccountRoleSelector.has_role(
                account_profile=self.account_profile,
                role_key="admin",
            )
        )
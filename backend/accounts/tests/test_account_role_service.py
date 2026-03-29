from django.test import TestCase

from accounts.models import AccountProfile, AccountRole, RoleDefinition
from accounts.services.account_role_service import AccountRoleService
from accounts.exceptions import RoleAlreadyAssignedError
from accounts.exceptions import InactiveRoleDefinitionError
from users.models.user import User
from websites.models.websites import Website


class AccountRoleServiceTests(TestCase):
    """Tests for account role assignment."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="Test UserName",
            email="role@example.com",
            password="password123",
        )
        self.profile = AccountProfile.objects.create(
            website=self.website,
            user=self.user,
        )
        self.role = RoleDefinition.objects.create(
            website=self.website,
            key="client",
            name="Client",
            is_system_role=True,
            is_active=True,
        )

    def test_assign_role(self):
        """It should assign a role to an account profile."""
        assigned_role = AccountRoleService.assign_role(
            account_profile=self.profile,
            role=self.role,
        )

        self.assertTrue(
            AccountRole.objects.filter(id=assigned_role.id).exists()
        )
        self.assertTrue(assigned_role.is_active)
        self.assertEqual(assigned_role.account_profile, self.profile)
        self.assertEqual(assigned_role.role, self.role)
        self.assertEqual(assigned_role.website, self.website)

    def test_assign_role_raises_when_role_already_assigned(self):
        """It should reject assigning an already active role."""
        AccountRoleService.assign_role(
            account_profile=self.profile,
            role=self.role,
        )

        with self.assertRaises(RoleAlreadyAssignedError):
            AccountRoleService.assign_role(
                account_profile=self.profile,
                role=self.role,
            )

    def test_assign_role_raises_for_inactive_role(self):
        """It should reject assignment of inactive roles."""
        self.role.is_active = False
        self.role.save(update_fields=["is_active"])

        with self.assertRaises(InactiveRoleDefinitionError):
            AccountRoleService.assign_role(
                account_profile=self.profile,
                role=self.role,
            )
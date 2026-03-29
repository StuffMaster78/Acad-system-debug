from django.test import TestCase

from accounts.models import AccountAuditLog, AccountProfile
from accounts.services.account_creation_service import (
    AccountCreationService,
)
from users.models.user import User
from websites.models.websites import Website


class AccountCreationServiceTests(TestCase):
    """Tests for account profile creation."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="Test Username",
            email="test@example.com",
            password="password123",
        )

    def test_create_account_profile(self):
        """It should create an account profile and audit log."""
        profile = AccountCreationService.create_account_profile(
            website=self.website,
            user=self.user,
        )

        self.assertTrue(
            AccountProfile.objects.filter(id=profile.id).exists()
        )
        self.assertTrue(
            AccountAuditLog.objects.filter(account_profile=profile).exists()
        )
        self.assertEqual(profile.website, self.website)
        self.assertEqual(profile.user, self.user)


    def test_create_account_profile_raises_for_duplicate(self):
        """It should reject duplicate account profiles."""
        AccountCreationService.create_account_profile(
            website=self.website,
            user=self.user,
        )

        with self.assertRaises(Exception):
            AccountCreationService.create_account_profile(
                website=self.website,
                user=self.user,
            )
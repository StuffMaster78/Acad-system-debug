from django.test import TestCase

from accounts.enums import AccountAuditEventType, AccountStatus
from accounts.exceptions import InvalidAccountStatusTransitionError
from accounts.models import (
    AccountAuditLog,
    AccountProfile,
    AccountStatusHistory,
)
from accounts.services.account_activation_service import (
    AccountActivationService,
)
from users.models.user import User
from websites.models.websites import Website


class AccountActivationServiceTests(TestCase):
    """Tests for account lifecycle actions."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="activation_user",
            email="activation@example.com",
            password="password123",
        )
        self.account_profile = AccountProfile.objects.create(
            website=self.website,
            user=self.user,
            status=AccountStatus.PENDING,
        )

    def test_activate_account(self):
        """It should activate a pending account profile."""
        updated_profile = AccountActivationService.activate_account(
            account_profile=self.account_profile,
        )

        updated_profile.refresh_from_db()

        self.assertEqual(updated_profile.status, AccountStatus.ACTIVE)
        self.assertIsNotNone(updated_profile.activated_at)
        self.assertIsNone(updated_profile.suspended_at)
        self.assertEqual(updated_profile.suspension_reason, "")

        self.assertTrue(
            AccountAuditLog.objects.filter(
                account_profile=updated_profile,
                event_type=AccountAuditEventType.ACCOUNT_ACTIVATED,
            ).exists()
        )

        self.assertTrue(
            AccountStatusHistory.objects.filter(
                account_profile=updated_profile,
                old_status=AccountStatus.PENDING,
                new_status=AccountStatus.ACTIVE,
            ).exists()
        )

    def test_suspend_account(self):
        """It should suspend an active account profile."""
        self.account_profile.status = AccountStatus.ACTIVE
        self.account_profile.save(update_fields=["status", "updated_at"])

        updated_profile = AccountActivationService.suspend_account(
            account_profile=self.account_profile,
            reason="Violation of platform rules.",
        )

        updated_profile.refresh_from_db()

        self.assertEqual(updated_profile.status, AccountStatus.SUSPENDED)
        self.assertIsNotNone(updated_profile.suspended_at)
        self.assertEqual(
            updated_profile.suspension_reason,
            "Violation of platform rules.",
        )

        self.assertTrue(
            AccountAuditLog.objects.filter(
                account_profile=updated_profile,
                event_type=AccountAuditEventType.ACCOUNT_SUSPENDED,
            ).exists()
        )

        self.assertTrue(
            AccountStatusHistory.objects.filter(
                account_profile=updated_profile,
                old_status=AccountStatus.ACTIVE,
                new_status=AccountStatus.SUSPENDED,
            ).exists()
        )

    def test_reactivate_account(self):
        """It should reactivate a suspended account profile."""
        self.account_profile.status = AccountStatus.SUSPENDED
        self.account_profile.suspension_reason = "Temporary suspension."
        self.account_profile.save(
            update_fields=["status", "suspension_reason", "updated_at"]
        )

        updated_profile = AccountActivationService.reactivate_account(
            account_profile=self.account_profile,
        )

        updated_profile.refresh_from_db()

        self.assertEqual(updated_profile.status, AccountStatus.ACTIVE)
        self.assertIsNone(updated_profile.suspended_at)
        self.assertEqual(updated_profile.suspension_reason, "")

        self.assertTrue(
            AccountAuditLog.objects.filter(
                account_profile=updated_profile,
                event_type=AccountAuditEventType.ACCOUNT_REACTIVATED,
            ).exists()
        )

        self.assertTrue(
            AccountStatusHistory.objects.filter(
                account_profile=updated_profile,
                old_status=AccountStatus.SUSPENDED,
                new_status=AccountStatus.ACTIVE,
            ).exists()
        )

    def test_suspend_account_raises_for_non_active_profile(self):
        """It should reject suspension for a non-active account."""
        with self.assertRaises(InvalidAccountStatusTransitionError):
            AccountActivationService.suspend_account(
                account_profile=self.account_profile,
                reason="Invalid suspend attempt.",
            )

    def test_reactivate_account_raises_for_non_suspended_profile(self):
        """It should reject reactivation for a non-suspended account."""
        with self.assertRaises(InvalidAccountStatusTransitionError):
            AccountActivationService.reactivate_account(
                account_profile=self.account_profile,
            )

    def test_activate_account_raises_for_already_active_profile(self):
        """It should reject activation for an already active account."""
        self.account_profile.status = AccountStatus.ACTIVE
        self.account_profile.save(update_fields=["status", "updated_at"])

        with self.assertRaises(InvalidAccountStatusTransitionError):
            AccountActivationService.activate_account(
                account_profile=self.account_profile,
            )
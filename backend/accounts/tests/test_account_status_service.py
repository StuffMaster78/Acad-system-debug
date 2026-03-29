from django.test import TestCase

from accounts.enums import AccountStatus
from accounts.exceptions import InvalidAccountStatusTransitionError
from accounts.models import AccountProfile, AccountStatusHistory
from accounts.services.account_status_service import AccountStatusService
from users.models.user import User
from websites.models.websites import Website


class AccountStatusServiceTests(TestCase):
    """Tests for generic account status transitions."""

    def setUp(self):
        self.website = Website.objects.create(name="Test Site")
        self.user = User.objects.create_user(
            username="status_user",
            email="status@example.com",
            password="password123",
        )
        self.account_profile = AccountProfile.objects.create(
            website=self.website,
            user=self.user,
            status=AccountStatus.PENDING,
        )

    def test_transition_status(self):
        """It should transition account status and create history."""
        updated_profile = AccountStatusService.transition_status(
            account_profile=self.account_profile,
            new_status=AccountStatus.ACTIVE,
            reason="Approved activation.",
        )

        updated_profile.refresh_from_db()

        self.assertEqual(updated_profile.status, AccountStatus.ACTIVE)

        self.assertTrue(
            AccountStatusHistory.objects.filter(
                account_profile=updated_profile,
                old_status=AccountStatus.PENDING,
                new_status=AccountStatus.ACTIVE,
                reason="Approved activation.",
            ).exists()
        )

    def test_transition_status_raises_for_invalid_transition(self):
        """It should reject invalid account status transitions."""
        self.account_profile.status = AccountStatus.DISABLED
        self.account_profile.save(update_fields=["status", "updated_at"])

        with self.assertRaises(InvalidAccountStatusTransitionError):
            AccountStatusService.transition_status(
                account_profile=self.account_profile,
                new_status=AccountStatus.ACTIVE,
                reason="Invalid reactivation.",
            )

    def test_transition_status_stores_metadata(self):
        """It should store metadata on account status history."""
        metadata = {"source": "test_case"}

        AccountStatusService.transition_status(
            account_profile=self.account_profile,
            new_status=AccountStatus.ACTIVE,
            reason="Approved activation.",
            metadata=metadata,
        )

        history = AccountStatusHistory.objects.get(
            account_profile=self.account_profile,
            old_status=AccountStatus.PENDING,
            new_status=AccountStatus.ACTIVE,
        )

        self.assertEqual(history.metadata, metadata)
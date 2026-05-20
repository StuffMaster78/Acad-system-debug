from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

from client_management.models import ClientProfile
from loyalty_management.models import LoyaltyTier
from loyalty_management.services.points_service import LoyaltyPointsService
from websites.models.websites import Website


User = get_user_model()


class LoyaltyPointsServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Gradecrest",
            domain="https://gradecrest.test",
        )
        self.user = User.objects.create_user(
            email="client@gradecrest.test",
            username="client",
            password="pass",
            role="client",
            website=self.website,
        )
        self.client_profile = ClientProfile.objects.create(
            user=self.user,
            website=self.website,
        )
        self.silver = LoyaltyTier.objects.create(
            website=self.website,
            name="Silver",
            threshold=100,
            discount_percentage=5,
        )

    @patch("notifications_system.services.notification_service.NotificationService.notify")
    def test_award_points_updates_balance_ledger_and_tier(self, _mock_notify):
        transaction = LoyaltyPointsService.award_points(
            client_profile=self.client_profile,
            website=self.website,
            points=125,
            reason="Referral reward",
        )

        self.client_profile.refresh_from_db()
        self.assertEqual(self.client_profile.loyalty_points, 125)
        self.assertEqual(self.client_profile.tier, self.silver)
        self.assertEqual(transaction.points, 125)
        self.assertEqual(transaction.transaction_type, "add")

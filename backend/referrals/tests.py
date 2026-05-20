from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from client_management.models import ClientProfile
from django.test import TestCase
from referrals.models import Referral, ReferralBonusConfig, ReferralCode
from referrals.services.referral_reward_service import ReferralRewardService
from users.models import User
from wallets.services.client_wallet_service import ClientWalletService
from websites.models.websites import Website


class ReferralModelTest(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Referral Model Site",
            domain="https://referral-model.test",
        )
        self.referrer = User.objects.create_user(
            email="referrer@test.local",
            username="referrer",
            website=self.website,
        )
        self.referee = User.objects.create_user(
            email="referee@test.local",
            username="referee",
            website=self.website,
        )

    def test_create_referral(self):
        referral = Referral.objects.create(
            website=self.website,
            referrer=self.referrer,
            referee=self.referee,
        )
        self.assertEqual(referral.referrer, self.referrer)
        self.assertEqual(referral.referee, self.referee)
        self.assertFalse(referral.registration_bonus_credited)

    def test_generate_referral_code(self):
        ReferralCode.objects.filter(user=self.referrer).delete()
        ReferralCode.objects.create(
            user=self.referrer,
            website=self.website,
            code="REF-12345",
        )
        self.assertEqual(self.referrer.referral_code.code, "REF-12345")

    def test_referral_code_waits_until_client_has_website(self):
        client = User.objects.create_user(
            email="late-site-client@test.local",
            username="late-site-client",
            role="client",
        )

        self.assertFalse(ReferralCode.objects.filter(user=client).exists())

        client.website = self.website
        client.save(update_fields=["website", "updated_at"])

        self.assertTrue(ReferralCode.objects.filter(user=client).exists())


class ReferralRewardServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Gradecrest",
            domain="https://gradecrest.test",
        )
        self.referrer = User.objects.create_user(
            email="referrer2@test.local",
            username="referrer2",
            password="pass",
            role="client",
            website=self.website,
        )
        self.referee = User.objects.create_user(
            email="referee2@test.local",
            username="referee2",
            password="pass",
            role="client",
            website=self.website,
        )
        self.referrer_profile = ClientProfile.objects.create(
            user=self.referrer,
            website=self.website,
        )
        self.referee_profile = ClientProfile.objects.create(
            user=self.referee,
            website=self.website,
        )
        self.referral = Referral.objects.create(
            website=self.website,
            referrer=self.referrer,
            referee=self.referee,
            referral_code="REF-TEST",
        )
        ReferralBonusConfig.objects.create(
            website=self.website,
            first_order_bonus=Decimal("5.00"),
            first_order_discount_amount=Decimal("0.00"),
            referrer_loyalty_points=80,
            referee_loyalty_points=20,
            award_wallet_bonus=True,
            award_loyalty_points=True,
        )

    @patch(
        "notifications_system.services.notification_service."
        "NotificationService.notify"
    )
    @patch.object(
        ReferralRewardService,
        "_is_first_qualifying_order",
        return_value=True,
    )
    def test_awards_wallet_and_loyalty_for_qualified_referral(
        self,
        _mock_first_order,
        _mock_notify,
    ):
        order = SimpleNamespace(
            id=123,
            website=self.website,
            client=self.referee,
            approved_at=object(),
            status="completed",
        )

        ReferralRewardService.award_for_qualifying_order(order=order)

        self.referral.refresh_from_db()
        self.referrer_profile.refresh_from_db()
        self.referee_profile.refresh_from_db()

        self.assertTrue(self.referral.bonus_awarded)
        self.assertEqual(self.referrer_profile.loyalty_points, 80)
        self.assertEqual(self.referee_profile.loyalty_points, 20)
        wallet = ClientWalletService.get_wallet(
            website=self.website,
            client=self.referrer,
        )
        self.assertEqual(wallet.available_balance, Decimal("5.00"))

        ReferralRewardService.award_for_qualifying_order(order=order)
        self.referrer_profile.refresh_from_db()
        self.assertEqual(self.referrer_profile.loyalty_points, 80)

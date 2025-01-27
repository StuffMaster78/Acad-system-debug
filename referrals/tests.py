from django.test import TestCase
from users.models import User
from .models import Referral, ReferralCode, ReferralBonusConfig


class ReferralModelTest(TestCase):
    def setUp(self):
        self.referrer = User.objects.create(username="referrer")
        self.referee = User.objects.create(username="referee", referred_by=self.referrer)

    def test_create_referral(self):
        referral = Referral.objects.create(referrer=self.referrer, referee=self.referee)
        self.assertEqual(referral.referrer, self.referrer)
        self.assertEqual(referral.referee, self.referee)
        self.assertFalse(referral.registration_bonus_credited)

    def test_generate_referral_code(self):
        ReferralCode.objects.create(user=self.referrer, code="REF-12345")
        self.assertEqual(self.referrer.referral_code.code, "REF-12345")

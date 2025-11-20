
from decimal import Decimal
from referrals.models import ReferralStats
from referrals.models import Referral
from referrals.models import ReferralCode
from referrals.models import ReferralBonusConfig
from django.db import transaction
from django.utils import timezone

class ReferralStatsService:
    @staticmethod
    @transaction.atomic
    def increment_referral_count(user):
        stats = user.referral_stats
        stats.referral_count += 1
        stats.save(update_fields=["referral_count"])

    @staticmethod
    @transaction.atomic
    def decrement_referral_count(user):
        stats = user.referral_stats
        stats.referral_count = max(0, stats.referral_count - 1)
        stats.save(update_fields=["referral_count"])
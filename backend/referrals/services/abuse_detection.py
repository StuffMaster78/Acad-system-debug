"""
Service for detecting referral system abuse.
"""
from django.db.models import Q, Count
from django.utils.timezone import now, timedelta
from referrals.models import Referral, ReferralAbuseFlag, ReferralCode
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL


class ReferralAbuseDetectionService:
    """
    Service to detect and flag potential abuse in the referral system.
    """
    
    @staticmethod
    def detect_self_referral(referral):
        """
        Detect if a user is trying to refer themselves.
        """
        if referral.referrer == referral.referee:
            ReferralAbuseFlag.objects.create(
                referral=referral,
                abuse_type='self_referral',
                reason=f"User {referral.referrer.username} attempted to refer themselves.",
                detected_by='system'
            )
            referral.is_flagged = True
            referral.flagged_reason = "Self-referral detected"
            referral.save()
            return True
        return False
    
    @staticmethod
    def detect_same_ip_referral(referral):
        """
        Detect if referrer and referee are using the same IP address.
        This could indicate the same person using multiple accounts.
        """
        if referral.referrer_ip and referral.referee_ip:
            if referral.referrer_ip == referral.referee_ip:
                ReferralAbuseFlag.objects.create(
                    referral=referral,
                    abuse_type='suspicious_ip',
                    reason=f"Referrer and referee share the same IP address: {referral.referrer_ip}",
                    detected_by='system'
                )
                referral.is_flagged = True
                referral.flagged_reason = "Same IP address detected"
                referral.save()
                return True
        return False
    
    @staticmethod
    def detect_multiple_accounts(referral):
        """
        Detect if a user has multiple accounts referring each other.
        Check for patterns like:
        - Same email domain with similar usernames
        - Same IP addresses across multiple accounts
        - Rapid account creation and referrals
        """
        # Check if referrer has multiple referrals from same IP
        recent_referrals = Referral.objects.filter(
            referrer=referral.referrer,
            referee_ip=referral.referee_ip,
            created_at__gte=now() - timedelta(days=7)
        ).exclude(id=referral.id)
        
        if recent_referrals.count() >= 3:
            ReferralAbuseFlag.objects.create(
                referral=referral,
                abuse_type='multiple_accounts',
                reason=f"Referrer {referral.referrer.username} has {recent_referrals.count()} referrals from the same IP within 7 days.",
                detected_by='system'
            )
            referral.is_flagged = True
            referral.flagged_reason = "Multiple accounts pattern detected"
            referral.save()
            return True
        
        # Check if referee has been referred multiple times
        referee_referrals = Referral.objects.filter(
            referee=referral.referee
        ).exclude(id=referral.id)
        
        if referee_referrals.count() > 0:
            ReferralAbuseFlag.objects.create(
                referral=referral,
                abuse_type='multiple_accounts',
                reason=f"Referee {referral.referee.username} has been referred {referee_referrals.count()} times (possible multiple accounts).",
                detected_by='system'
            )
            referral.is_flagged = True
            referral.flagged_reason = "Referee has multiple referral records"
            referral.save()
            return True
        
        return False
    
    @staticmethod
    def detect_rapid_referrals(referral):
        """
        Detect if a user is making referrals too rapidly (potential bot/automation).
        """
        # Check for rapid referrals from same referrer
        recent_referrals = Referral.objects.filter(
            referrer=referral.referrer,
            created_at__gte=now() - timedelta(hours=1)
        ).exclude(id=referral.id)
        
        if recent_referrals.count() >= 5:
            ReferralAbuseFlag.objects.create(
                referral=referral,
                abuse_type='rapid_referrals',
                reason=f"Referrer {referral.referrer.username} made {recent_referrals.count()} referrals in the last hour.",
                detected_by='system'
            )
            referral.is_flagged = True
            referral.flagged_reason = "Rapid referral pattern detected"
            referral.save()
            return True
        
        return False
    
    @staticmethod
    def check_all_abuse_patterns(referral):
        """
        Run all abuse detection checks on a referral.
        Returns list of detected abuse types.
        """
        detected = []
        
        if ReferralAbuseDetectionService.detect_self_referral(referral):
            detected.append('self_referral')
        
        if ReferralAbuseDetectionService.detect_same_ip_referral(referral):
            detected.append('suspicious_ip')
        
        if ReferralAbuseDetectionService.detect_multiple_accounts(referral):
            detected.append('multiple_accounts')
        
        if ReferralAbuseDetectionService.detect_rapid_referrals(referral):
            detected.append('rapid_referrals')
        
        return detected
    
    @staticmethod
    def void_referral(referral, voided_by, reason):
        """
        Void a referral due to abuse. This prevents bonuses from being awarded.
        """
        referral.is_voided = True
        referral.voided_at = now()
        referral.voided_by = voided_by
        referral.flagged_reason = reason
        referral.save()
        
        # Update all related abuse flags
        ReferralAbuseFlag.objects.filter(
            referral=referral,
            status='pending'
        ).update(status='resolved')
        
        logger.info(f"Referral {referral.id} voided by {voided_by.username}: {reason}")
    
    @staticmethod
    def get_abuse_statistics(website=None):
        """
        Get statistics about referral abuse.
        """
        queryset = ReferralAbuseFlag.objects.all()
        if website:
            queryset = queryset.filter(referral__website=website)
        
        return {
            'total_flags': queryset.count(),
            'pending_review': queryset.filter(status='pending').count(),
            'resolved': queryset.filter(status='resolved').count(),
            'false_positives': queryset.filter(status='false_positive').count(),
            'by_type': queryset.values('abuse_type').annotate(
                count=Count('id')
            ).order_by('-count'),
        }


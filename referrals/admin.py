from django.contrib import admin
from django.db.models import Count, Sum, Q, F
from django.utils.html import format_html
from .models import (
    Referral, ReferralBonusConfig, ReferralCode, ReferralStats, ReferralBonusDecay
)
from client_wallet.models import WalletTransaction
from loyalty_management.models import LoyaltyTransaction


# Bulk Actions
def mark_bonus_awarded(modeladmin, request, queryset):
    """Mark selected referrals as bonus awarded."""
    queryset.update(bonus_awarded=True)
mark_bonus_awarded.short_description = "Mark as Bonus Awarded"


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referee', 'referral_code', 'created_at', 
                    'registration_bonus_credited', 'first_order_bonus_credited',
                    'website', 'completed_orders_count'
    )
    search_fields = ('referrer__username', 'referee__username',
                     'referral_code', 'website__domain'
    )
    list_filter = ('registration_bonus_credited',
                   'first_order_bonus_credited', 'website'
    )
    readonly_fields = ('created_at',)
    list_select_related = ('referrer', 'referee', 'website')
    actions = [mark_bonus_awarded, "detect_fraud", "award_loyalty_bonus"]

    def completed_orders_count(self, obj):
        """Shows how many referrals led to a completed order that was paid"""
        return obj.referee.orders.filter(status='completed', payment_status='paid').count()
    completed_orders_count.short_description = "Completed Paid Orders from Referrals"

    def detect_fraud(self, request, queryset):
        """Identifies possible fraudulent referrals"""

        # Self-referral fraud
        self_referrals = queryset.filter(referrer=Q(referee__username=F('referrer__username')))
        
        # High referrals with no activity
        high_referrals = queryset.annotate(referral_count=Count('referrer__referrals')).filter(
            referral_count__gt=10, referee__orders__isnull=True
        )

        flagged_referrals = self_referrals.union(high_referrals)
        self.message_user(request, f"{flagged_referrals.count()} suspicious referrals detected.")

    def award_loyalty_bonus(self, request, queryset):
        """Awards loyalty points and processes wallet transactions for referral bonuses"""
        for referral in queryset.filter(bonus_awarded=True):
            client_wallet = referral.referrer.wallet
            bonus_config = referral.website.referralbonusconfig

            bonus_amount = bonus_config.first_order_bonus if bonus_config else 0

            # Check if the referral bonus should be awarded based on first paid order
            first_paid_order = referral.referee.orders.filter(status='completed', payment_status='paid').first()
            if first_paid_order:
                # Add bonus to wallet
                WalletTransaction.objects.create(
                    wallet=client_wallet,
                    amount=bonus_amount,
                    transaction_type="credit",
                    reason="Referral bonus for referring {}".format(referral.referee.username)
                )

                # Log transaction in loyalty management
                LoyaltyTransaction.objects.create(
                    client=referral.referrer,
                    points=int(bonus_amount),  # Convert bonus to points if needed
                    transaction_type="add",
                    reason="Referral reward for {}".format(referral.referee.username)
                )
                
                # Award the bonus
                referral.bonus_awarded = True
                referral.save()
            
        self.message_user(request, "Referral bonuses successfully awarded!")
    award_loyalty_bonus.short_description = "Award Referral Bonuses"


@admin.register(ReferralBonusConfig)
class ReferralBonusConfigAdmin(admin.ModelAdmin):
    list_display = ('website', 'first_order_bonus',
                    'max_referrals_per_month',
                    'max_referral_bonus_per_month'
    )
    search_fields = ('website__domain',)
    list_filter = ('website',)


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'website')
    search_fields = ('user__username', 'code', 'website__domain')
    list_filter = ('website',)


@admin.register(ReferralStats)
class ReferralStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_referrals', 'successful_referrals',
                    'referral_bonus_earned', 'last_referral_at'
    )
    search_fields = ('user__username',)
    list_filter = ('last_referral_at',)


@admin.register(ReferralBonusDecay)
class ReferralBonusDecayAdmin(admin.ModelAdmin):
    list_display = ("wallet_transaction", "decay_rate", "decay_start_at")
    search_fields = ("wallet_transaction__id",)
    list_filter = ("decay_start_at")
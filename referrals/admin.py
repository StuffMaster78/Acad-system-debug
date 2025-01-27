from django.contrib import admin
from .models import Referral, ReferralBonusConfig, ReferralCode


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referee', 'referral_code', 'created_at', 'registration_bonus_credited', 'first_order_bonus_credited', 'website')
    search_fields = ('referrer__username', 'referee__username', 'referral_code')
    list_filter = ('registration_bonus_credited', 'first_order_bonus_credited', 'website')


@admin.register(ReferralBonusConfig)
class ReferralBonusConfigAdmin(admin.ModelAdmin):
    list_display = ('website', 'registration_bonus', 'first_order_bonus', 'referee_discount')
    search_fields = ('website__name',)


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'website')
    search_fields = ('user__username', 'code')
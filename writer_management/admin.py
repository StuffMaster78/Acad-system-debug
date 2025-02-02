from django.contrib import admin
from django.utils.html import format_html
from .models import (
    WriterProfile, WriterLevel, WriterConfig, WriterOrderRequest, WriterOrderTake,
    WriterPayoutPreference, WriterPayment, PaymentHistory, WriterEarningsHistory,
    WriterEarningsReviewRequest, WriterReward, WriterRewardCriteria, Probation,
    WriterPenalty, WriterSuspension, WriterActionLog, WriterSupportTicket,
    WriterDeadlineExtensionRequest, WriterOrderHoldRequest, WriterOrderReopenRequest,
    WriterActivityLog, WriterRatingCooldown, WriterFileDownloadLog, WriterIPLog
)


### ---------------- Writer Profile Admin ---------------- ###

@admin.register(WriterProfile)
class WriterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'registration_id', 'writer_level', 'completed_orders', 'total_earnings', 'verification_status')
    list_filter = ('writer_level', 'verification_status', 'location_verified')
    search_fields = ('user__username', 'registration_id', 'email')
    readonly_fields = ('joined', 'last_logged_in', 'wallet_balance', 'average_rating')
    
    def wallet_balance(self, obj):
        return f"${obj.wallet_balance():,.2f}"
    wallet_balance.short_description = "Wallet Balance"

    def average_rating(self, obj):
        return f"{obj.average_rating():.2f}" if obj.average_rating() else "N/A"
    average_rating.short_description = "Avg. Rating"


### ---------------- Writer Level Admin ---------------- ###

@admin.register(WriterLevel)
class WriterLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_orders', 'base_pay_per_page', 'urgency_percentage_increase', 'tip_percentage')
    list_filter = ('max_orders',)
    search_fields = ('name',)


### ---------------- Admin Configuration ---------------- ###

@admin.register(WriterConfig)
class WriterConfigAdmin(admin.ModelAdmin):
    list_display = ('takes_enabled', 'max_requests_per_writer')
    list_editable = ('takes_enabled', 'max_requests_per_writer')


### ---------------- Order Request & Take ---------------- ###

@admin.register(WriterOrderRequest)
class WriterOrderRequestAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'requested_at', 'approved', 'reviewed_by')
    list_filter = ('approved',)
    search_fields = ('writer__user__username', 'order__id')
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, f"✅ Approved {queryset.count()} order requests.")
    approve_requests.short_description = "Approve Selected Requests"


@admin.register(WriterOrderTake)
class WriterOrderTakeAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'taken_at')
    search_fields = ('writer__user__username', 'order__id')


### ---------------- Payments & Earnings ---------------- ###

@admin.register(WriterPayoutPreference)
class WriterPayoutPreferenceAdmin(admin.ModelAdmin):
    list_display = ('writer', 'preferred_method', 'payout_threshold')
    list_filter = ('preferred_method',)


@admin.register(WriterPayment)
class WriterPaymentAdmin(admin.ModelAdmin):
    list_display = ('writer', 'amount', 'payment_date', 'bonuses', 'fines', 'tips')
    list_filter = ('payment_date',)
    search_fields = ('writer__user__username',)


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('writer', 'amount', 'payment_date', 'bonuses', 'fines', 'tips')
    list_filter = ('payment_date',)
    search_fields = ('writer__user__username',)


@admin.register(WriterEarningsHistory)
class WriterEarningsHistoryAdmin(admin.ModelAdmin):
    list_display = ('writer', 'period_start', 'period_end', 'total_earnings', 'orders_completed')
    list_filter = ('period_start', 'period_end')
    search_fields = ('writer__user__username',)


@admin.register(WriterEarningsReviewRequest)
class WriterEarningsReviewRequestAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'requested_at', 'resolved')
    list_filter = ('resolved',)
    search_fields = ('writer__user__username', 'order__id')


### ---------------- Rewards & Penalties ---------------- ###

@admin.register(WriterReward)
class WriterRewardAdmin(admin.ModelAdmin):
    list_display = ('writer', 'title', 'awarded_date', 'prize')
    search_fields = ('writer__user__username', 'title')


@admin.register(WriterRewardCriteria)
class WriterRewardCriteriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_completed_orders', 'min_rating', 'min_earnings', 'auto_reward_enabled')


@admin.register(Probation)
class ProbationAdmin(admin.ModelAdmin):
    list_display = ('writer', 'placed_by', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('writer__user__username',)


@admin.register(WriterPenalty)
class WriterPenaltyAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'reason', 'amount_deducted', 'created_at')
    list_filter = ('reason',)
    search_fields = ('writer__user__username',)


@admin.register(WriterSuspension)
class WriterSuspensionAdmin(admin.ModelAdmin):
    list_display = ('writer', 'reason', 'suspended_by', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)


### ---------------- Support, Requests & Disputes ---------------- ###

@admin.register(WriterSupportTicket)
class WriterSupportTicketAdmin(admin.ModelAdmin):
    list_display = ('writer', 'category', 'status', 'created_at', 'updated_at')
    list_filter = ('category', 'status')


@admin.register(WriterDeadlineExtensionRequest)
class WriterDeadlineExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'old_deadline', 'requested_deadline', 'approved')
    list_filter = ('approved',)


@admin.register(WriterOrderHoldRequest)
class WriterOrderHoldRequestAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'requested_at', 'approved')


@admin.register(WriterOrderReopenRequest)
class WriterOrderReopenRequestAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'requested_at', 'approved')


### ---------------- Activity Logs & Tracking ---------------- ###

@admin.register(WriterActivityLog)
class WriterActivityLogAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'action_type', 'timestamp')
    list_filter = ('action_type',)
    search_fields = ('writer__user__username',)


@admin.register(WriterRatingCooldown)
class WriterRatingCooldownAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'cooldown_until', 'rating_allowed')
    list_filter = ('rating_allowed',)


@admin.register(WriterFileDownloadLog)
class WriterFileDownloadLogAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'file_name', 'downloaded_at')


@admin.register(WriterIPLog)
class WriterIPLogAdmin(admin.ModelAdmin):
    list_display = ('writer', 'ip_address', 'logged_at')
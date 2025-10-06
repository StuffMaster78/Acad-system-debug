from django.contrib import admin
from django.utils.html import format_html
from writer_management.models.status import WriterStatus
from writer_management.models.profile import (
    WriterProfile, WriterEducation
)
from writer_management.models.levels import WriterLevel
from writer_management.models.configs import WriterConfig
from writer_management.models.requests import (
    WriterOrderHoldRequest, WriterOrderReopenRequest,
    WriterDeadlineExtensionRequest, WriterOrderRequest,
    WriterOrderTake, WriterEarningsReviewRequest
)
from writer_management.models.tickets import WriterSupportTicket
from writer_management.models.payout import  (
    WriterPayoutPreference,
    WriterEarningsHistory,
    WriterPayment
)
from writer_management.models.rewards import (
    WriterReward, WriterRewardCriteria
)
from writer_management.models.discipline import (
    Probation, WriterPenalty, WriterSuspension
)
from writer_management.models.writer_warnings import WriterWarning
from writer_management.models.file_management import (
    WriterFile, WriterFileVersion,
    WriterFileAccessRequest,
    WriterFileActivityLog
)

from writer_management.models.logs import (
    WriterActionLog,
    WriterActivityLog, WriterFileDownloadLog,
    WriterIPLog, WriterActivityTracking
)


from writer_management.models.ratings import (
    WriterRating,
    WriterRatingFeedback,
    WriterRatingCooldown
)
### ---------------- Writer Profile Admin ---------------- ###

@admin.register(WriterProfile)
class WriterProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'registration_id', 'writer_level',
        'completed_orders', 'total_earnings',
        'verification_status'
    )
    list_filter = ('writer_level', 'verification_status', 'location_verified')
    search_fields = ('user__username', 'registration_id', 'email')
    readonly_fields = ('joined_at', 'last_logged_in', 'wallet_balance', 'average_rating')
    
    def wallet_balance(self, obj):
        return f"${obj.wallet_balance():,.2f}"
    wallet_balance.short_description = "Wallet Balance"

    def average_rating(self, obj):
        return f"{obj.average_rating():.2f}" if obj.average_rating() else "N/A"
    average_rating.short_description = "Avg. Rating"


### ---------------- Writer Level Admin ---------------- ###

@admin.register(WriterLevel)
class WriterLevelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'max_orders', 'base_pay_per_page',
        'urgency_percentage_increase', 'tip_percentage'
    )
    list_filter = ('max_orders',)
    search_fields = ('name',)


@admin.register(WriterEducation)
class WriterEducationAdmin(admin.ModelAdmin):
    list_display = ('writer', 'degree', 'institution_name', 'academic_level', 'graduation_year')
    search_fields = ('writer__user__username', 'degree', 'institution_name', 'academic_level')


@admin.register(WriterActivityTracking)
class WriterActivityTrackingAdmin(admin.ModelAdmin):
    list_display = ('writer', 'last_login', 'last_seen', 'created_at')
    search_fields = ('writer__user__username', 'activity')

@admin.register(WriterActionLog)
class WriterActionLogAdmin(admin.ModelAdmin):
    list_display = ('writer', 'action', 'created_at')
    search_fields = ('writer__user__username', 'action')

### ---------------- Admin Configuration ---------------- ###
@admin.register(WriterConfig)
class WriterConfigAdmin(admin.ModelAdmin):
    list_display = ('takes_enabled', 'max_requests_per_writer')
    # list_editable = ('takes_enabled', 'max_requests_per_writer')
    # list_display_links = ('takes_enabled',)  # Add a clickable field for the row



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


@admin.register(WriterEarningsHistory)
class WriterEarningsHistoryAdmin(admin.ModelAdmin):
    list_display = ('writer', 'period_start', 'period_end', 'total_earnings', 'orders_completed')
    list_filter = ('period_start', 'period_end')
    search_fields = ('writer__user__username',)


@admin.register(WriterEarningsReviewRequest)
class WriterEarningsReviewRequestAdmin(admin.ModelAdmin):
    list_display = ('writer', 'order', 'requested_at', 'approved')
    list_filter = ('approved',)
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
    list_display = ('writer', 'order', 'file', 'downloaded_at')


@admin.register(WriterIPLog)
class WriterIPLogAdmin(admin.ModelAdmin):
    list_display = ('writer', 'ip_address', 'logged_at')


@admin.register(WriterStatus)
class WriterStatusAdmin(admin.ModelAdmin):
    list_display = (
        "writer", "website", "strikes", "is_suspended",
        "is_blacklisted", "is_on_probation", "updated_at",
        "is_active", "last_strike_at", "suspension_ends_at",
        "probation_ends_at", "active_strikes"
    )
    readonly_fields = (
        "writer", "website", "strikes", "is_suspended",
        "is_blacklisted", "is_on_probation", "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    

@admin.register(WriterWarning)
class WriterWarningAdmin(admin.ModelAdmin):
    list_display = ['writer', 'warning_type', 'is_active', 'expires_at']
    list_filter = ['warning_type', 'is_active']
    search_fields = ['writer__user__username', 'reason']


@admin.register(WriterFile)
class WriterFileAdmin(admin.ModelAdmin):
    list_display = ['writer', 'order', 'file_name', 'uploaded_at', 'is_active']
    list_filter = ['is_active']
    search_fields = ['writer__user__username', 'file_name']

@admin.register(WriterFileVersion)
class WriterFileVersionAdmin(admin.ModelAdmin):
    list_display = ['file', 'version_number', 'uploaded_at']
    list_filter = ['file', 'version_number']
    search_fields = ['file__file_name', 'version_number']
    ordering = ['-uploaded_at']

@admin.register(WriterFileAccessRequest)
class WriterFileAccessRequestAdmin(admin.ModelAdmin):
    list_display = ['writer', 'order', 'requested_at', 'status']
    list_filter = ['status']
    search_fields = ['writer__user__username', 'order__id']
    ordering = ['-requested_at']

@admin.register(WriterFileActivityLog)
class WriterFileActivityLogAdmin(admin.ModelAdmin):
    list_display = ['writer', 'order', 'action', 'occurred_at']
    list_filter = ['action']
    search_fields = ['writer__user__username', 'order__id']
    ordering = ['-occurred_at']


@admin.register(WriterRating)
class WriterRatingAdmin(admin.ModelAdmin):
    list_display = ('writer', 'client', 'order', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('writer__user__username', 'client__username', 'order__id')

@admin.register(WriterRatingFeedback)
class WriterRatingFeedbackAdmin(admin.ModelAdmin):
    list_display = ('rating', 'comment', 'created_at')
    search_fields = ('rating__writer__user__username', 'comment')
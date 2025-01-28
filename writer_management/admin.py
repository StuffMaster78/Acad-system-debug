from django.contrib import admin
from .models import (
    WriterProfile,
    WriterLevel,
    WriterLeave,
    WriterActionLog,
    WriterEducation,
    PaymentHistory,
    WriterReward,
    WriterRating,
)

@admin.register(WriterProfile)
class WriterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'registration_id', 'writer_level', 'completed_orders', 'total_earnings', 'verification_status')
    search_fields = ('user__username', 'registration_id', 'email')
    list_filter = ('writer_level', 'verification_status', 'website')
    readonly_fields = ('total_earnings', 'completed_orders', 'average_rating')

@admin.register(WriterLevel)
class WriterLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_orders', 'base_pay_per_page', 'base_pay_per_slide', 'tip_percentage')
    search_fields = ('name',)

@admin.register(WriterLeave)
class WriterLeaveAdmin(admin.ModelAdmin):
    list_display = ('writer', 'start_date', 'end_date', 'reason', 'approved')
    list_filter = ('approved',)

@admin.register(WriterActionLog)
class WriterActionLogAdmin(admin.ModelAdmin):
    list_display = ('writer', 'action', 'reason', 'created_at')
    list_filter = ('action',)

@admin.register(WriterEducation)
class WriterEducationAdmin(admin.ModelAdmin):
    list_display = ('writer', 'institution_name', 'degree', 'graduation_year', 'is_verified')
    list_filter = ('is_verified',)

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('writer', 'amount', 'bonuses', 'fines', 'tips', 'payment_date')
    list_filter = ('payment_date',)

@admin.register(WriterReward)
class WriterRewardAdmin(admin.ModelAdmin):
    list_display = ('writer', 'title', 'awarded_date', 'prize')
    list_filter = ('awarded_date',)

@admin.register(WriterRating)
class WriterRatingAdmin(admin.ModelAdmin):
    list_display = ('writer', 'client', 'order', 'rating', 'created_at')
    list_filter = ('rating',)
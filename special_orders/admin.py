from django.contrib import admin
from .models import PredefinedSpecialOrderConfig, SpecialOrder, Milestone, ProgressLog, WriterBonus


@admin.register(PredefinedSpecialOrderConfig)
class PredefinedSpecialOrderConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'cost', 'is_active')
    search_fields = ('name',)
    list_filter = ('website', 'is_active')


@admin.register(SpecialOrder)
class SpecialOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'website', 'client', 'writer', 'order_type', 'status', 'total_cost', 'created_at')
    list_filter = ('website', 'status', 'order_type', 'created_at')
    search_fields = ('id', 'client__email', 'writer__email')


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'special_order', 'website', 'due_date', 'is_completed')
    list_filter = ('website', 'is_completed', 'due_date')
    search_fields = ('name',)


@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
    list_display = ('special_order', 'writer', 'website', 'progress_date', 'description')
    list_filter = ('website', 'progress_date')
    search_fields = ('special_order__id', 'writer__email')


@admin.register(WriterBonus)
class WriterBonusAdmin(admin.ModelAdmin):
    list_display = ('writer', 'special_order', 'website', 'amount', 'category', 'is_paid')
    list_filter = ('website', 'is_paid', 'category')
    search_fields = ('writer__email',)
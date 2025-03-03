from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from import_export.admin import ExportMixin
from import_export import resources
from .models import Referral, ReferralBonusConfig, ReferralCode


# Export Referral Data as CSV
class ReferralResource(resources.ModelResource):
    class Meta:
        model = Referral
        fields = ('referrer__username', 'referee__username', 'referral_code', 'created_at', 
                  'registration_bonus_credited', 'first_order_bonus_credited', 'website__domain')


# Bulk Actions
def mark_registration_bonus_credited(modeladmin, request, queryset):
    queryset.update(registration_bonus_credited=True)
mark_registration_bonus_credited.short_description = "Mark as Registration Bonus Credited"

def mark_first_order_bonus_credited(modeladmin, request, queryset):
    queryset.update(first_order_bonus_credited=True)
mark_first_order_bonus_credited.short_description = "Mark as First Order Bonus Credited"


@admin.register(Referral)
class ReferralAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ReferralResource
    list_display = ('referrer', 'referee', 'referral_code', 'created_at', 
                    'registration_bonus_credited', 'first_order_bonus_credited', 'website', 'completed_orders_count')
    search_fields = ('referrer__username', 'referee__username', 'referral_code', 'website__domain')
    list_filter = ('registration_bonus_credited', 'first_order_bonus_credited', 'website')
    readonly_fields = ('created_at',)
    list_select_related = ('referrer', 'referee', 'website')
    actions = [mark_registration_bonus_credited, mark_first_order_bonus_credited]

    def completed_orders_count(self, obj):
        """Shows how many referrals led to a completed order"""
        return obj.referrals.filter(first_order_bonus_credited=True).count()
    completed_orders_count.short_description = "Completed Orders"


@admin.register(ReferralBonusConfig)
class ReferralBonusConfigAdmin(admin.ModelAdmin):
    list_display = ('website', 'registration_bonus', 'first_order_bonus', 'referee_discount')
    search_fields = ('website__domain',)
    list_filter = ('website',)


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'website')
    search_fields = ('user__username', 'code', 'website__domain')
    list_filter = ('website',)


# Custom Reports
class ReferralReportsAdmin(admin.ModelAdmin):
    change_list_template = "admin/referral_reports.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # 📊 Top Referrers
        extra_context["top_referrers"] = Referral.objects.values("referrer__username") \
            .annotate(total_referrals=Count("id")) \
            .order_by("-total_referrals")[:5]

        # 💰 Top Earners
        extra_context["top_earners"] = Referral.objects.values("referrer__username") \
            .annotate(total_earned=Sum("registration_bonus_credited")) \
            .order_by("-total_earned")[:5]

        # ✅ Most Completed Orders
        extra_context["most_completed_orders"] = Referral.objects.values("referrer__username") \
            .annotate(completed_orders=Count("id", filter=Count("first_order_bonus_credited"))) \
            .order_by("-completed_orders")[:5]

        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Referral, ReferralReportsAdmin)
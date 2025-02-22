from django.contrib import admin
from .models import SuperadminProfile, SuperadminLog

@admin.register(SuperadminProfile)
class SuperadminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "can_manage_users", "can_manage_payments", "can_view_reports")
    search_fields = ("user__username", "user__email")
    list_filter = ("can_manage_users", "can_manage_payments")

@admin.register(SuperadminLog)
class SuperadminLogAdmin(admin.ModelAdmin):
    list_display = ("superadmin", "action", "timestamp")
    search_fields = ("superadmin__username", "action")
    list_filter = ("timestamp",)
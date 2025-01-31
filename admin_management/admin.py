from django.contrib import admin
from .models import AdminProfile, AdminLog

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "can_manage_writers", "can_manage_support", "can_manage_editors", "can_suspend_users")
    search_fields = ("user__username", "user__email")
    list_filter = ("can_manage_writers", "can_suspend_users")

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ("admin", "action", "timestamp")
    search_fields = ("admin__username", "action")
    list_filter = ("timestamp",)
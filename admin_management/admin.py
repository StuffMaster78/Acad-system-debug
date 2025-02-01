from django.contrib import admin
from .models import AdminProfile, AdminLog

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_superadmin", "can_manage_writers", "can_manage_clients", "can_handle_orders")
    search_fields = ("user__username", "user__email")
    list_filter = ("is_superadmin", "can_manage_writers", "can_manage_clients")

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ("admin", "action", "target_user", "order", "timestamp")
    search_fields = ("admin__username", "action", "target_user__username")
    list_filter = ("timestamp",)
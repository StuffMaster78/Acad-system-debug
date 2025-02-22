from django.contrib import admin
from .models import ActivityLog

class UserFilter(admin.SimpleListFilter):
    """Custom filter to filter logs by user."""
    title = "User"
    parameter_name = "user"

    def lookups(self, request, model_admin):
        users = set(ActivityLog.objects.filter(user__isnull=False).values_list("user__id", "user__username"))
        return [(user_id, username) for user_id, username in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset

class ActionTypeFilter(admin.SimpleListFilter):
    """Custom filter to filter logs by action type."""
    title = "Action Type"
    parameter_name = "action_type"

    def lookups(self, request, model_admin):
        action_types = set(ActivityLog.objects.values_list("action_type", flat=True))
        return [(action, action) for action in action_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(action_type=self.value())
        return queryset

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action_type", "description", "timestamp", "metadata_preview")
    list_filter = (UserFilter, ActionTypeFilter, "timestamp")  # ✅ Custom filters added
    search_fields = ("user__username", "description", "metadata")
    ordering = ("-timestamp",)
    readonly_fields = ("user", "action_type", "description", "timestamp", "metadata")

    def metadata_preview(self, obj):
        """Show a preview of metadata in the admin list view."""
        return obj.metadata if obj.metadata else "N/A"
    
    metadata_preview.short_description = "Metadata"

    def has_add_permission(self, request):
        """Prevent manual addition of logs from the admin panel."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent modification of logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow admins to delete logs if needed."""
        return True  # Optional, set to False if you want logs to be permanent
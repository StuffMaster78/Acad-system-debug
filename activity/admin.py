from django.contrib import admin
from activity.models import ActivityLog
import json
import csv
from django.http import HttpResponse
from django.utils.html import format_html, escape

class UserFilter(admin.SimpleListFilter):
    """Custom filter to filter logs by user."""
    title = "User"
    parameter_name = "user"

    def lookups(self, request, model_admin):
        users = ActivityLog.objects.filter(user__isnull=False).values_list(
            "user__id", "user__username"
        ).distinct()
        return [(uid, uname) for uid, uname in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset


class ActionTypeFilter(admin.SimpleListFilter):
    """Custom filter to filter logs by action type."""
    title = "Action Type"
    parameter_name = "action_type"

    def lookups(self, request, model_admin):
        actions = ActivityLog.objects.values_list(
            "action_type", flat=True
        ).distinct()
        return [(a, a) for a in actions]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(action_type=self.value())
        return queryset


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "timestamp",
        "action_type",
        "user",
        "triggered_by",
        "website",
        "short_description",
        "metadata_preview",
        "related_object_link",
    )
    list_filter = (
        UserFilter,
        ActionTypeFilter,
        "website",
        "timestamp",
    )
    search_fields = (
        "description",
        "user__username",
        "triggered_by__username",
        "metadata",
    )
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)
    readonly_fields = (
        "timestamp",
        "user",
        "triggered_by",
        "action_type",
        "description",
        "website",
        "metadata",
        "ip_address",
        "user_agent",
    )

    def short_description(self, obj):
        return obj.description[:60] + "..." if len(obj.description) > 60 else obj.description

    short_description.short_description = "Description"

    def metadata_preview(self, obj):
        """Render truncated metadata for quick glance."""
        preview = str(obj.metadata)
        return preview[:75] + "..." if len(preview) > 75 else preview

    metadata_preview.short_description = "Metadata"

    def has_add_permission(self, request):
        return False  # Disallow adding logs manually

    def has_change_permission(self, request, obj=None):
        return False  # Disallow editing logs

    def has_delete_permission(self, request, obj=None):
        return True  # Or False, if logs should be immutable
    
    def metadata_preview(self, obj):
        """Render nicely formatted metadata for admin."""
        if not obj.metadata:
            return "—"

        try:
            pretty = json.dumps(obj.metadata, indent=2)
            return format_html(
                "<pre style='white-space: pre-wrap; max-height: 200px; overflow: auto;'>{}</pre>",
                escape(pretty),
            )
        except Exception:
            return str(obj.metadata)
        
    def related_object_link(self, obj):
        """Try to link to a related object in admin if known."""
        from django.apps import apps
        from django.urls import reverse
        from django.utils.safestring import mark_safe

        model_name = obj.metadata.get("related_model")  # e.g. "orders.Order"
        obj_id = obj.metadata.get("related_id")

        if model_name and obj_id:
            try:
                app_label, model = model_name.lower().split(".")
                model_class = apps.get_model(app_label, model)
                url = reverse(f"admin:{app_label}_{model}_change", args=[obj_id])
                return mark_safe(f"<a href='{url}'>View {model} #{obj_id}</a>")
            except Exception:
                return f"{model_name} #{obj_id}"

        return "—"

    related_object_link.short_description = "Related Object"


    def export_as_csv(self, request, queryset):
        """Export selected activity logs as CSV."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="activity_logs.csv"'
        )

        writer = csv.writer(response)
        writer.writerow([
            "ID", "User", "Triggered By", "Action Type",
            "Description", "Timestamp", "Metadata",
        ])
        for obj in queryset:
            writer.writerow([
                obj.id,
                str(obj.user),
                str(obj.triggered_by),
                obj.action_type,
                obj.description,
                obj.timestamp.isoformat(),
                json.dumps(obj.metadata),
            ])
        return response


    export_as_csv.short_description = "Export selected logs as CSV"
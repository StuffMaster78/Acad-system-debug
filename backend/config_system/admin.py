from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from config_system.audit.models import ConfigAuditLog
from config_system.storage.models import ConfigItem


# ============================================================
# Config Item Admin
# ============================================================

@admin.register(ConfigItem)
class ConfigItemAdmin(admin.ModelAdmin):

    list_display = (
        "key",
        "scope",
        "environment",
        "is_active",
        "website_scope",
        "tenant_scope",
        "user_scope",
        "updated_at",
    )

    list_filter = (
        "scope",
        "environment",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "key",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_modified_at",
        "created_by",
        "updated_by",
    )

    ordering = (
        "key",
    )

    list_per_page = 50

    save_on_top = True

    fieldsets = (
        (
            "Core",
            {
                "fields": (
                    "key",
                    "value",
                    "scope",
                    "environment",
                    "is_active",
                )
            },
        ),
        (
            "Scope",
            {
                "fields": (
                    "website_id",
                    "tenant_id",
                    "user_id",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                    "last_modified_at",
                )
            },
        ),
    )

    # --------------------------------------------------------
    # Scope Indicators
    # --------------------------------------------------------

    @admin.display(
        description="Website",
        ordering="website_id",
    )
    def website_scope(
        self,
        obj: ConfigItem,
    ) -> str:

        if obj.website_id is None:
            return "—"

        return str(obj.website_id)

    @admin.display(
        description="Tenant",
        ordering="tenant_id",
    )
    def tenant_scope(
        self,
        obj: ConfigItem,
    ) -> str:

        if obj.tenant_id is None:
            return "—"

        return str(obj.tenant_id)

    @admin.display(
        description="User",
        ordering="user_id",
    )
    def user_scope(
        self,
        obj: ConfigItem,
    ) -> str:

        if obj.user_id is None:
            return "—"

        return str(obj.user_id)

    # --------------------------------------------------------
    # Audit Attribution
    # --------------------------------------------------------

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ) -> None:

        if not obj.pk:
            obj.created_by = request.user

        obj.updated_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change,
        )


# ============================================================
# Audit Log Admin
# ============================================================

@admin.register(ConfigAuditLog)
class ConfigAuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "key",
        "action_badge",
        "scope",
        "environment",
        "changed_by",
        "created_at",
    )

    list_filter = (
        "action",
        "scope",
        "environment",
        "created_at",
    )

    search_fields = (
        "key",
        "reason",
    )

    readonly_fields = (
        "config_item",
        "key",
        "scope",
        "environment",
        "action",
        "old_value",
        "new_value",
        "changed_by",
        "reason",
        "metadata",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 100

    date_hierarchy = "created_at"

    # --------------------------------------------------------
    # Immutable Audit Logs
    # --------------------------------------------------------

    def has_add_permission(
        self,
        request,
    ) -> bool:

        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ) -> bool:

        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ) -> bool:

        return False

    # --------------------------------------------------------
    # Visual Action Labels
    # --------------------------------------------------------

    @admin.display(
        description="Action",
        ordering="action",
    )
    def action_badge(
        self,
        obj: ConfigAuditLog,
    ):

        color_map = {
            "create": "#2563eb",
            "update": "#f59e0b",
            "delete": "#dc2626",
        }

        color = color_map.get(
            obj.action,
            "#6b7280",
        )

        return format_html(
            """
            <span style="
                background: {};
                color: white;
                padding: 4px 8px;
                border-radius: 6px;
                font-weight: 600;
            ">
                {}
            </span>
            """,
            color,
            obj.action.upper(),
        )
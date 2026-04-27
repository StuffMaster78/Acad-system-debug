from django.contrib import admin

from accounts.models import (
    AccountAuditLog,
    AccountProfile,
    AccountRole,
    AccountStatusHistory,
    OnboardingSession,
    RoleDefinition,
    PermissionDefinition,
    RolePermission,
    PortalDefinition,
    PortalAccess,
    TenantAccess,
)


@admin.register(AccountProfile)
class AccountProfileAdmin(admin.ModelAdmin):
    """Admin configuration for account profiles."""

    list_display = (
        "id",
        "website",
        "user",
        "status",
        "onboarding_status",
        "is_primary",
        "activated_at",
        "created_at",
    )
    list_filter = (
        "website",
        "status",
        "onboarding_status",
        "is_primary",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "activated_at",
        "suspended_at",
    )
    ordering = ("-created_at",)


@admin.register(RoleDefinition)
class RoleDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for role definitions."""

    list_display = (
        "id",
        "website",
        "key",
        "name",
        "is_system_role",
        "is_active",
        "created_at",
    )
    list_filter = (
        "website",
        "is_system_role",
        "is_active",
    )
    search_fields = (
        "key",
        "name",
        "description",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = ("name",)


@admin.register(AccountRole)
class AccountRoleAdmin(admin.ModelAdmin):
    """Admin configuration for account role assignments."""

    list_display = (
        "id",
        "website",
        "account_profile",
        "role",
        "is_active",
        "assigned_by",
        "assigned_at",
        "expires_at",
    )
    list_filter = (
        "website",
        "is_active",
        "role",
    )
    search_fields = (
        "account_profile__user__email",
        "account_profile__user__username",
        "role__key",
        "role__name",
    )
    readonly_fields = (
        "assigned_at",
    )
    ordering = ("-assigned_at",)


@admin.register(AccountAuditLog)
class AccountAuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for account audit logs."""

    list_display = (
        "id",
        "website",
        "user",
        "account_profile",
        "event_type",
        "actor",
        "created_at",
    )
    list_filter = (
        "website",
        "event_type",
    )
    search_fields = (
        "user__email",
        "user__username",
        "description",
    )
    readonly_fields = (
        "created_at",
    )
    ordering = ("-created_at",)


@admin.register(AccountStatusHistory)
class AccountStatusHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for account status history."""

    list_display = (
        "id",
        "website",
        "account_profile",
        "old_status",
        "new_status",
        "changed_by",
        "created_at",
    )
    list_filter = (
        "website",
        "old_status",
        "new_status",
    )
    search_fields = (
        "account_profile__user__email",
        "account_profile__user__username",
        "reason",
    )
    readonly_fields = (
        "created_at",
    )
    ordering = ("-created_at",)


@admin.register(OnboardingSession)
class OnboardingSessionAdmin(admin.ModelAdmin):
    """Admin configuration for onboarding sessions."""

    list_display = (
        "id",
        "website",
        "user",
        "account_profile",
        "onboarding_type",
        "target_role",
        "status",
        "started_at",
        "completed_at",
        "expires_at",
    )
    list_filter = (
        "website",
        "onboarding_type",
        "status",
        "target_role",
    )
    search_fields = (
        "user__email",
        "user__username",
        "last_step",
    )
    readonly_fields = (
        "started_at",
        "completed_at",
        "updated_at",
    )
    ordering = ("-started_at",)


@admin.register(PermissionDefinition)
class PermissionDefinitionAdmin(admin.ModelAdmin):
    list_display = ("code", "is_active")
    search_fields = ("code",)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission", "is_active")
    list_filter = ("role",)


@admin.register(PortalDefinition)
class PortalDefinitionAdmin(admin.ModelAdmin):
    list_display = ("code", "domain", "is_active")


@admin.register(PortalAccess)
class PortalAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "portal", "is_active")


@admin.register(TenantAccess)
class TenantAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "website", "is_active")
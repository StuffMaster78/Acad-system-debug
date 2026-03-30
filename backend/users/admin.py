from django.contrib import admin

from users.models import (
    ProfileReminder,
    ProfileReminderStatus,
    ProfileReminderType,
    ProfileUpdateRequest,
    User,
    UserProfile,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "website",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "website",
    )
    search_fields = (
        "email",
        "username",
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "display_name",
        "country",
        "timezone",
        "updated_at",
    )
    search_fields = (
        "user__email",
        "display_name",
    )
    list_select_related = (
        "user",
    )


@admin.register(ProfileUpdateRequest)
class ProfileUpdateRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "status",
        "reviewed_by",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "website",
    )
    search_fields = (
        "user__email",
        "reviewed_by__email",
    )
    list_select_related = (
        "user",
        "website",
        "profile",
        "reviewed_by",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "applied_at",
        "reviewed_at",
    )


@admin.register(ProfileReminder)
class ProfileReminderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "reminder_type",
        "channel",
        "status",
        "sent_at",
    )
    list_filter = (
        "reminder_type",
        "status",
        "channel",
        "website",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    list_select_related = (
        "user",
        "website",
    )
    readonly_fields = (
        "sent_at",
    )
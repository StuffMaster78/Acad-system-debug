from django.contrib import admin

from privacy.models import CookieConsentRecord, ExitIntentPopupConfig


@admin.register(CookieConsentRecord)
class CookieConsentRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "user",
        "anonymous_id",
        "preferences",
        "analytics",
        "marketing",
        "source",
        "created_at",
        "revoked_at",
    )
    list_filter = (
        "website",
        "preferences",
        "analytics",
        "marketing",
        "source",
        "revoked_at",
        "created_at",
    )
    search_fields = (
        "anonymous_id",
        "user__email",
        "website__name",
        "source_host",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "ip_hash",
        "user_agent_hash",
    )
    date_hierarchy = "created_at"


@admin.register(ExitIntentPopupConfig)
class ExitIntentPopupConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "website",
        "is_enabled",
        "trigger",
        "title",
        "primary_cta_label",
        "updated_at",
    )
    list_filter = ("is_enabled", "trigger", "requires_marketing_consent", "website")
    search_fields = ("website__name", "title", "body", "primary_cta_label")
    readonly_fields = ("created_at", "updated_at")

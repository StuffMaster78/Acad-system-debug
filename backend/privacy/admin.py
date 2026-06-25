from django.contrib import admin

from privacy.models import CookieConsentRecord, ExitIntentPopupConfig, WebsiteCookieConfig


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
    fieldsets = (
        ("Site", {
            "fields": ("website", "is_enabled"),
        }),
        ("Content", {
            "description": "What the popup says. Leave image_url blank for a text-only popup.",
            "fields": ("title", "body", "image_url"),
        }),
        ("Call to action", {
            "fields": ("primary_cta_label", "primary_cta_url", "secondary_cta_label"),
        }),
        ("Trigger", {
            "description": (
                "exit_intent fires when the cursor leaves the top of the viewport. "
                "delay fires after N seconds. scroll_depth fires after scrolling past a percentage."
            ),
            "fields": ("trigger", "delay_seconds", "scroll_depth_percent"),
        }),
        ("Frequency & paths", {
            "fields": (
                "cooldown_hours",
                "max_shows_per_session",
                "requires_marketing_consent",
                "show_on_paths",
                "suppress_on_paths",
            ),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(WebsiteCookieConfig)
class WebsiteCookieConfigAdmin(admin.ModelAdmin):
    list_display = (
        "website",
        "consent_version",
        "policy_version",
        "marketing_available",
        "updated_at",
    )
    list_filter = ("marketing_available", "website")
    search_fields = ("website__name", "consent_version", "policy_version")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Tenant", {"fields": ("website",)}),
        (
            "Consent versions",
            {
                "description": (
                    "Bumping either version string forces all visitors to re-consent "
                    "the next time they visit the site."
                ),
                "fields": ("consent_version", "policy_version"),
            },
        ),
        (
            "Policy URLs",
            {
                "description": "Relative or absolute links used in the cookie banner.",
                "fields": ("privacy_policy_url", "cookie_policy_url"),
            },
        ),
        (
            "Feature flags",
            {"fields": ("marketing_available",)},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

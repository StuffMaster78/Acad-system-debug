from django.contrib import admin
from django.utils.html import format_html

from .models import HelpArticle, HelpCategory, LegalDocument, UserAgreement


# ────────────────────────────────────────────────────────────────────────────
# Legal documents
# ────────────────────────────────────────────────────────────────────────────

@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title", "doc_type", "version", "effective_date",
        "active_badge", "requires_re_acceptance", "website", "created_at",
    )
    list_filter = ("doc_type", "is_active", "requires_re_acceptance", "website")
    search_fields = ("title", "version")
    readonly_fields = ("created_at", "updated_at", "created_by", "content_preview")
    ordering = ("-effective_date",)
    save_on_top = True

    fieldsets = (
        ("Document identity", {
            "fields": ("website", "doc_type", "title", "version", "effective_date"),
        }),
        ("Content", {
            "fields": ("content", "content_preview"),
            "description": (
                "Paste full HTML content or write plain text. "
                "Supported tags: &lt;h2&gt;, &lt;h3&gt;, &lt;p&gt;, "
                "&lt;ul&gt;/&lt;ol&gt;/&lt;li&gt;, &lt;strong&gt;, &lt;em&gt;, &lt;a&gt;."
            ),
        }),
        ("Activation", {
            "fields": ("is_active", "requires_re_acceptance"),
            "description": (
                "Tick 'Is active' to publish this version. "
                "Any previously active version of the same type will be archived automatically."
            ),
        }),
        ("Metadata", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;font-weight:bold">● ACTIVE</span>')
        return format_html('<span style="color:#aaa">archived</span>')
    active_badge.short_description = "Status"

    def content_preview(self, obj):
        if not obj.content:
            return "—"
        from django.utils.html import strip_tags
        return format_html(
            '<div style="max-height:300px;overflow-y:auto;border:1px solid #ddd;padding:12px;white-space:pre-wrap">{}</div>',
            strip_tags(obj.content[:3000]),
        )
    content_preview.short_description = "Content preview"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        if obj.is_active:
            obj.activate()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["content"].widget.attrs.update({
            "rows": 35,
            "style": "font-family:monospace;font-size:13px;",
        })
        return form


@admin.register(UserAgreement)
class UserAgreementAdmin(admin.ModelAdmin):
    list_display = ("user", "document", "agreed_at", "ip_address")
    list_filter = ("document__doc_type", "document__website")
    search_fields = ("user__email", "user__username", "ip_address")
    readonly_fields = ("user", "document", "agreed_at", "ip_address", "user_agent")
    ordering = ("-agreed_at",)

    def has_add_permission(self, request):
        return False # Agreements are created by the system, not manually


# ────────────────────────────────────────────────────────────────────────────
# Help center
# ────────────────────────────────────────────────────────────────────────────

class HelpArticleInline(admin.TabularInline):
    model = HelpArticle
    fields = ("title", "slug", "audience", "is_published", "order")
    extra = 0
    ordering = ("order",)


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title", "slug", "audience", "icon",
        "article_count", "is_active", "order", "website",
    )
    list_filter = ("audience", "is_active", "website")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    inlines = [HelpArticleInline]

    def article_count(self, obj):
        return obj.articles.filter(is_published=True).count()
    article_count.short_description = "Published articles"


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title", "category", "audience", "is_published",
        "is_featured", "order", "updated_at",
    )
    list_filter = ("audience", "is_published", "is_featured", "category", "website")
    search_fields = ("title", "slug", "summary")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    ordering = ("category", "order", "title")
    save_on_top = True

    fieldsets = (
        ("Article", {
            "fields": (
                "website", "category", "title", "slug",
                "summary", "audience", "order",
            ),
        }),
        ("Content", {
            "fields": ("content",),
            "description": (
                "Write in HTML. Supported: "
                "&lt;h2&gt;, &lt;h3&gt;, &lt;p&gt;, &lt;ul&gt;/&lt;ol&gt;/&lt;li&gt;, "
                "&lt;strong&gt;, &lt;em&gt;, &lt;a href&gt;, &lt;code&gt;, &lt;blockquote&gt;."
            ),
        }),
        ("Visibility", {
            "fields": ("is_published", "is_featured"),
        }),
        ("Metadata", {
            "fields": ("created_by", "updated_by", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["content"].widget.attrs.update({
            "rows": 40,
            "style": "font-family:monospace;font-size:13px;",
        })
        return form

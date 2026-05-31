"""
Wagtail hooks for cms_attachments.
Tenant-scoped snippet admin for Attachments and AttachmentCategories.
"""

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet

from cms_attachments.models import Attachment, AttachmentCategory
from cms_core.services.tenant_service import filter_queryset_by_user_sites


class AttachmentCategorySnippetViewSet(SnippetViewSet):
    model = AttachmentCategory
    icon = "folder"
    menu_label = "Attachment Categories"
    menu_name = "attachment-categories"
    menu_order = 400
    list_display = ["name", "slug", "site", "display_order"]
    list_filter = ["site"]
    search_fields = ["name"]

    def get_queryset(self, request=None):
        qs = super().get_queryset()
        return filter_queryset_by_user_sites(qs, self.request.user)


class AttachmentSnippetViewSet(SnippetViewSet):
    model = Attachment
    icon = "doc-full"
    menu_label = "Attachments"
    menu_name = "attachments"
    menu_order = 410
    add_to_admin_menu = True
    list_display = [
        "title",
        "attachment_type",
        "gate_type",
        "academic_level",
        "status",
        "download_count",
        "is_featured",
        "site",
    ]
    list_filter = [
        "attachment_type",
        "gate_type",
        "status",
        "academic_level",
        "is_featured",
        "site",
    ]
    search_fields = ["title", "description", "subject_area"]
    ordering = ["-is_featured", "-download_count"]

    def get_queryset(self, request=None):
        qs = super().get_queryset()
        return filter_queryset_by_user_sites(qs, self.request.user)


# Re-register with custom viewsets
try:
    from wagtail.snippets.models import SNIPPET_MODELS

    for model in [Attachment, AttachmentCategory]:
        if model in SNIPPET_MODELS:
            SNIPPET_MODELS.remove(model)
except Exception:
    pass

register_snippet(AttachmentCategorySnippetViewSet)
register_snippet(AttachmentSnippetViewSet)
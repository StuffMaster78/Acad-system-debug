"""
Wagtail hooks for cms_references.
Tenant-scoped Reference snippet admin.
"""

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet

from cms_references.models import Reference, ReferenceTag
from cms_core.services.tenant_service import filter_queryset_by_user_sites


class ReferenceSnippetViewSet(SnippetViewSet):
    model = Reference
    icon = "link-external"
    menu_label = "References"
    menu_name = "references"
    menu_order = 350
    add_to_admin_menu = True
    list_display = [
        "title",
        "reference_type",
        "publication_year",
        "quality_tier",
        "is_verified",
        "is_url_dead",
        "usage_count",
        "site",
    ]
    list_filter = [
        "reference_type",
        "quality_tier",
        "is_verified",
        "is_peer_reviewed",
        "is_url_dead",
        "site",
    ]
    search_fields = [
        "title",
        "journal_name",
        "organization",
        "doi",
        "pmid",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_queryset_by_user_sites(qs, self.request.user)


# Re-register with custom viewsets
try:
    from wagtail.snippets.models import SNIPPET_MODELS

    for model in [Reference, ReferenceTag]:
        if model in SNIPPET_MODELS:
            SNIPPET_MODELS.remove(model)
except Exception:
    pass

register_snippet(ReferenceSnippetViewSet)
# ReferenceTag stays with default registration — it's global, not tenant-scoped
register_snippet(ReferenceTag)
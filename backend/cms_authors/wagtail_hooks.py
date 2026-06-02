"""
Wagtail hooks for cms_authors.
Registers the Author snippet with tenant-scoped filtering.
"""

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet

from cms_authors.models import Author
from cms_core.services.tenant_service import filter_queryset_by_user_sites


class AuthorSnippetViewSet(SnippetViewSet):
    """Tenant-scoped Author admin.

    Non-superusers only see authors belonging to their permitted sites.
    """

    model = Author
    icon = "user"
    menu_label = "Authors"
    menu_name = "authors"
    menu_order = 200
    add_to_admin_menu = True
    list_display = [
        "name",
        "credentials",
        "role",
        "site",
        "is_active",
        "show_publicly",
    ]
    list_filter = ["role", "is_active", "show_publicly", "site"]
    search_fields = ["name", "bio", "areas_of_expertise", "credentials"]
    ordering = ["display_order", "name"]

    def get_queryset(self, request=None):
        qs = super().get_queryset(request)
        if not request:
            return qs
        return filter_queryset_by_user_sites(qs, request.user)


# Re-register with the custom viewset
# (unregister the default registration from models.py first)
try:
    from wagtail.snippets.models import SNIPPET_MODELS

    if Author in SNIPPET_MODELS:
        SNIPPET_MODELS.remove(Author)
except Exception:
    pass

register_snippet(AuthorSnippetViewSet)
"""
Wagtail hooks for cms_references.
Tenant-scoped Reference snippet admin.
"""

from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel

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

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("site"),
                FieldPanel("reference_type"),
            ],
            heading="Source & Tenant",
        ),

        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel(
                    "authors",
                    help_text=(
                        'JSON list of author objects. '
                        'Example: [{"family": "Smith", "given": "J.", "middle": "A."}]'
                    ),
                ),
                FieldRowPanel([
                    FieldPanel("publication_year"),
                    FieldPanel("publication_month"),
                ]),
            ],
            heading="Bibliographic Identity",
        ),

        MultiFieldPanel(
            [
                FieldPanel("journal_name"),
                FieldRowPanel([
                    FieldPanel("journal_volume"),
                    FieldPanel("journal_issue"),
                    FieldPanel("pages"),
                ]),
                FieldPanel("publisher"),
                FieldPanel("publisher_location"),
                FieldPanel("organization"),
            ],
            heading="Publication Details",
            classname="collapsed",
        ),

        MultiFieldPanel(
            [
                FieldPanel("doi"),
                FieldRowPanel([
                    FieldPanel("isbn"),
                    FieldPanel("issn"),
                    FieldPanel("pmid"),
                ]),
            ],
            heading="Identifiers",
            classname="collapsed",
        ),

        MultiFieldPanel(
            [
                FieldPanel("url"),
                FieldPanel("url_archived"),
                FieldRowPanel([
                    FieldPanel("is_url_dead"),
                    FieldPanel("last_verified"),
                ]),
            ],
            heading="URLs & Link Status",
        ),

        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel("is_open_access"),
                    FieldPanel("is_peer_reviewed"),
                    FieldPanel("is_verified"),
                ]),
                FieldPanel("quality_tier"),
                FieldPanel("tags"),
            ],
            heading="Quality & Trust",
        ),

        FieldPanel("internal_notes"),
    ]

    def get_queryset(self, request=None):
        qs = super().get_queryset(request)
        if not request:
            return qs
        return filter_queryset_by_user_sites(qs, request.user)


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

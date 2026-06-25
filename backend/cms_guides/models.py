"""
CMS Guides
===========

Wagtail-backed guides and training materials for the staff portal.

Structure per site:
  GuideIndexPage  (one per site, slug = "guides")
    └── GuideArticlePage  (individual guide/training doc)

Each guide has:
- audience targeting (all / client / writer / staff)
- full RichTextField body (Wagtail WYSIWYG — headings, lists, links, images)
- optional PDF attachment via Wagtail Documents
- icon (Lucide name) and featured flag for the portal listing

Staff author and manage guides entirely through Wagtail CMS admin.
The portal fetches them via /cms-api/guides/.
"""

from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.search import index
from rest_framework import serializers as drf_serializers


class GuideAudience(models.TextChoices):
    ALL    = "all",    "All users"
    CLIENT = "client", "Clients"
    WRITER = "writer", "Writers"
    STAFF  = "staff",  "Staff & Admins"


class _PdfSerializer(drf_serializers.Serializer):
    """Expose the PDF document URL (and title) in the API response."""
    def to_representation(self, doc):
        if doc is None:
            return None
        return {
            "title": doc.title,
            "url":   doc.url,
        }


# ── Index page ────────────────────────────────────────────────────────────────

class GuideIndexPage(Page):
    """One per site — the parent of all GuideArticlePage objects."""

    subpage_types  = ["cms_guides.GuideArticlePage"]
    parent_page_types = ["wagtailcore.Page"]
    max_count_per_parent = 1

    promote_panels = Page.promote_panels

    class Meta:
        verbose_name = "Guide index"

    def __str__(self):
        return self.title


# ── Article page ──────────────────────────────────────────────────────────────

class GuideArticlePage(Page):
    """A single guide or training document."""

    summary = models.CharField(
        max_length=300,
        blank=True,
        help_text="One-line description shown on the guides listing page.",
    )
    body = RichTextField(
        help_text=(
            "Full guide content. Use headings (H2/H3), bullet lists, numbered "
            "steps, bold/italic, links, and embedded images."
        )
    )
    audience = models.CharField(
        max_length=20,
        choices=GuideAudience.choices,
        default=GuideAudience.STAFF,
        db_index=True,
        help_text=(
            "Who can see this guide in the portal. "
            "'Staff & Admins' covers superadmin, admin, editor, and support roles."
        ),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="book-open",
        help_text="Lucide icon name shown on the listing card (e.g. 'book-open', 'users', 'settings').",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured guides appear prominently on the guides home screen.",
    )
    estimated_read_minutes = models.PositiveSmallIntegerField(
        default=5,
        help_text="Estimated reading time in minutes.",
    )
    pdf_attachment = models.ForeignKey(
        "wagtaildocs.Document",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text=(
            "Optional downloadable PDF — training handbooks, SOPs, checklists. "
            "Upload via Documents in the Wagtail admin sidebar."
        ),
    )

    parent_page_types = ["cms_guides.GuideIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("audience"),
                FieldPanel("icon"),
                FieldPanel("is_featured"),
                FieldPanel("estimated_read_minutes"),
            ],
            heading="Settings",
        ),
        FieldPanel("summary"),
        FieldPanel("body"),
        FieldPanel("pdf_attachment"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
    ]

    api_fields = [
        APIField("summary"),
        APIField("body"),
        APIField("audience"),
        APIField("icon"),
        APIField("is_featured"),
        APIField("estimated_read_minutes"),
        APIField("pdf_attachment", serializer=_PdfSerializer()),
    ]

    class Meta:
        verbose_name = "Guide article"
        verbose_name_plural = "Guide articles"

    def __str__(self):
        return self.title

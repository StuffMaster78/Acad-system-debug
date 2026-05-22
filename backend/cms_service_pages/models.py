"""
CMS Service Pages
==================

Service pages (landing pages) are the bottom of the conversion funnel.
Each represents one monetized offering. 15-30 per tenant at maturity.

Their job: convert visitors into orders. Every block on the page
must earn its place toward conversion.

ServicePage is a Wagtail Page type with a deliberately smaller,
more opinionated block library than blog posts.
"""

from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.search import index

from cms_core.blocks import SERVICE_PAGE_BLOCKS


class ServiceIndexPage(Page):
    """Container page for service pages. One per tenant site.
    Can live at /services/ or be hidden (service pages can also
    live directly under TenantHomePage for clean URLs)."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["cms_service_pages.ServicePage"]
    parent_page_types = ["cms_core.TenantHomePage"]

    api_fields = [APIField("intro")]

    class Meta:
        verbose_name = "Service Index Page"


class ServicePage(Page):
    """A single service / landing page. Bottom-of-funnel conversion.

    Funnel: BlogPostPage → ServicePage → Order.

    Block library is deliberately small and opinionated.
    If an editor wants something not in the library, evaluate
    whether the page actually needs it before building a new block.
    """

    # --- Service details ---
    service_category = models.ForeignKey(
        "cms_core.ServiceCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_pages",
    )
    pricing_from = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Starting price per page (USD)",
    )
    pricing_to = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum price per page (USD)",
    )
    turnaround_hours_fastest = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fastest turnaround in hours (e.g., 3 for 3-hour delivery)",
    )
    turnaround_hours_standard = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Standard turnaround in hours (e.g., 168 for 7-day delivery)",
    )

    # --- Conversion mechanics ---
    primary_cta_text = models.CharField(
        max_length=100,
        default="Order Now",
        help_text="Text on the primary call-to-action button",
    )
    primary_cta_url = models.CharField(
        max_length=255,
        default="/order/",
        help_text="Destination URL or path for the primary CTA",
    )
    show_aggregate_rating = models.BooleanField(
        default=True,
        help_text="Display aggregate rating from reviews in Schema.org markup",
    )

    # --- Trust / review ---
    reviewer = models.ForeignKey(
        "cms_authors.Author",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_services",
        help_text="'Last reviewed by [Author] on [date]'",
    )

    # --- Content ---
    body = StreamField(
        SERVICE_PAGE_BLOCKS,
        use_json_field=True,
        blank=True,
    )

    # --- Freshness ---
    last_substantive_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Updated only when content substance changes. "
            "Drives Schema.org dateModified and freshness alerts."
        ),
    )

    # --- Panels ---
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("service_category"),
                FieldPanel("pricing_from"),
                FieldPanel("pricing_to"),
                FieldPanel("turnaround_hours_fastest"),
                FieldPanel("turnaround_hours_standard"),
            ],
            heading="Service Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_cta_text"),
                FieldPanel("primary_cta_url"),
                FieldPanel("show_aggregate_rating"),
                FieldPanel("reviewer"),
            ],
            heading="Conversion",
        ),
        FieldPanel("body"),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("last_substantive_update"),
    ]

    # --- Subpage rules ---
    subpage_types = []  # Service pages have no children
    parent_page_types = ["cms_service_pages.ServiceIndexPage"]

    # --- Search indexing ---
    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.FilterField("service_category"),
        index.FilterField("first_published_at"),
    ]

    # --- API exposure ---
    api_fields = [
        APIField("service_category"),
        APIField("pricing_from"),
        APIField("pricing_to"),
        APIField("turnaround_hours_fastest"),
        APIField("turnaround_hours_standard"),
        APIField("primary_cta_text"),
        APIField("primary_cta_url"),
        APIField("show_aggregate_rating"),
        APIField("reviewer"),
        APIField("body"),
        APIField("last_substantive_update"),
    ]

    class Meta:
        verbose_name = "Service Page"
        verbose_name_plural = "Service Pages"

    def __str__(self):
        return self.title
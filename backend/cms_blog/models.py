"""
CMS Blog
=========

Blog posts are the top of the conversion funnel.
Their job: acquire search traffic, build topical authority,
route readers toward service pages.

BlogPostPage is a Wagtail Page type.
Wagtail handles: title, slug, seo_title, search_description,
draft/live, revisions, scheduled publishing, moderation, search indexing.

We add: author, category, tags, featured image, excerpt, body (StreamField),
funnel routing (primary_service, pillar), citation mode, freshness tracking.
"""

from django import forms
from django.db import models

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from rest_framework import serializers as drf_serializers
from wagtail.models import Page, Orderable
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.api import APIField
from wagtail.search import index

from cms_core.blocks import BLOG_BLOCKS


class _CategoryNameSerializer(drf_serializers.Serializer):
    def to_representation(self, category):
        if category is None:
            return None
        return getattr(category, "name", str(category))


class _ThumbnailSerializer(drf_serializers.Serializer):
    def to_representation(self, image):
        if image is None:
            return None
        try:
            return {"url": image.get_rendition("width-800").url}
        except Exception:
            url = getattr(getattr(image, "file", None), "url", None)
            return {"url": url} if url else None


class BlogIndexPage(Page):
    """Container page for blog posts. One per tenant site.
    Lives at /blog/. Lists published posts."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["cms_blog.BlogPostPage"]
    parent_page_types = ["cms_core.TenantHomePage"]

    api_fields = [
        APIField("intro"),
    ]

    class Meta:
        verbose_name = "Blog Index Page"

    def get_context(self, request):
        context = super().get_context(request)
        context["posts"] = (
            self.get_children()
            .live()
            .specific()
            .order_by("-first_published_at")
        )
        return context


class BlogPostPage(Page):
    """A single blog post. Top-of-funnel content.

    Funnel: BlogPostPage → ServicePage → Order.

    Everything Wagtail gives us for free:
    - title, slug, seo_title, search_description (meta)
    - first_published_at, last_published_at
    - live (draft/published state)
    - has_unpublished_changes
    - locked (edit lock)
    - Revision history
    - Scheduled publishing (go_live_at)
    - Moderation workflow
    - URL routing (/blog/<slug>/)
    - Search indexing
    """

    # --- Authorship (non-negotiable per 2026 strategy) ---
    primary_author = models.ForeignKey(
        "cms_authors.Author",
        on_delete=models.PROTECT,
        related_name="blog_posts",
        help_text="Required. The named, credentialed author of this post.",
    )
    contributing_authors = ParentalManyToManyField(
        "cms_authors.Author",
        blank=True,
        related_name="contributed_posts",
    )

    # --- Categorization ---
    category = models.ForeignKey(
        "cms_core.BlogCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts",
    )
    tags = ParentalManyToManyField(
        "cms_core.BlogTag",
        blank=True,
        related_name="blog_posts",
    )

    # --- Content ---
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="Primary image for listings, social sharing, and Schema.org",
    )
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        help_text="Brief summary for listings and social sharing (max 300 chars)",
    )
    body = StreamField(
        BLOG_BLOCKS,
        use_json_field=True,
        blank=True,
    )

    # --- References / citation mode ---
    CITATION_MODE_CHOICES = [
        ("sources_list", "Simple sources list (default)"),
        ("formal_apa7", "Formal citations — APA 7"),
        ("formal_mla9", "Formal citations — MLA 9"),
        ("formal_chicago", "Formal citations — Chicago"),
        ("none", "No sources / references"),
    ]
    citation_mode = models.CharField(
        max_length=20,
        choices=CITATION_MODE_CHOICES,
        default="sources_list",
        help_text="How references are displayed at the bottom of the post",
    )

    # --- Funnel routing ---
    primary_service = models.ForeignKey(
        "cms_service_pages.ServicePage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_post_sources",
        help_text="The service page this blog post primarily routes readers toward",
    )
    pillar = models.ForeignKey(
        "cms_content_graph.ContentPillar",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="spoke_posts",
        help_text="Which content pillar / funnel this post feeds",
    )

    # --- Editorial reviewer ---
    reviewer = models.ForeignKey(
        "cms_authors.Author",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_posts",
        help_text="Expert who reviewed this post for accuracy — shown in editorial transparency section.",
    )

    # --- Lead magnet ---
    lead_magnet = models.ForeignKey(
        "cms_attachments.Attachment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts",
        help_text=(
            "Optional: attach a gated resource (cheat sheet, template, guide) that "
            "appears after the article body. Leave blank to show no download offer."
        ),
    )

    # --- Content migration ---
    original_published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Fill this in ONLY when migrating content from another site. "
            "Overrides Wagtail's first_published_at for display and Schema.org. "
            "Leave blank for new content — Wagtail sets the date automatically."
        ),
    )
    original_source_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="The canonical URL of this article on the source site (for records only — not displayed publicly).",
    )

    # --- Freshness tracking ---
    last_substantive_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Updated only when content substance changes, not metadata. "
            "Drives Schema.org dateModified and freshness alerts."
        ),
    )

    # --- Panels ---
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("primary_author"),
                FieldPanel(
                    "contributing_authors",
                    widget=forms.CheckboxSelectMultiple,
                ),
            ],
            heading="Authors",
        ),
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("tags", widget=forms.CheckboxSelectMultiple),
            ],
            heading="Categorization",
        ),
        FieldPanel("featured_image"),
        FieldPanel("excerpt"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("citation_mode"),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("primary_service"),
                FieldPanel("pillar"),
            ],
            heading="Funnel Routing",
        ),
        FieldPanel("last_substantive_update"),
        FieldPanel("reviewer"),
        FieldPanel(
            "lead_magnet",
            help_text="Choose a cheat sheet or guide to offer readers after this article. Leave blank to hide the download form.",
        ),
        MultiFieldPanel(
            [
                FieldPanel("original_published_at"),
                FieldPanel("original_source_url"),
            ],
            heading="Content Migration",
            help_text=(
                "Use these fields when importing an article that was previously "
                "published on another site. The original date will replace "
                "Wagtail's automatic first_published_at everywhere it is displayed."
            ),
        ),
    ]

    # --- Subpage rules ---
    subpage_types = [] # Blog posts have no children
    parent_page_types = ["cms_blog.BlogIndexPage"]

    # --- Search indexing ---
    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.SearchField("body"),
        index.FilterField("category"),
        index.FilterField("primary_author"),
        index.FilterField("first_published_at"),
    ]

    # --- API exposure ---
    api_fields = [
        APIField("primary_author"),
        APIField("contributing_authors"),
        APIField("category"),
        APIField("tags"),
        APIField("featured_image"),
        APIField("excerpt"),
        APIField("body"),
        APIField("citation_mode"),
        APIField("primary_service"),
        APIField("pillar"),
        APIField("last_substantive_update"),
        APIField("reviewer"),
        APIField("original_published_at"),
        APIField("canonical_published_at"),
        # Frontend-friendly aliases used by gradecrest-web and other marketing sites
        APIField("author_name"),
        APIField("author_credentials"),
        APIField("author_bio"),
        APIField("reading_time_minutes"),
        APIField("word_count"),
        APIField("tag_names"),
        APIField("thumbnail", serializer=_ThumbnailSerializer()),
        APIField("category_name", serializer=_CategoryNameSerializer()),
        APIField("views_count"),
        APIField("likes_count"),
        APIField("page_content_type_id"),
    ]

    @property
    def author_name(self) -> str:
        author = getattr(self, "primary_author", None)
        return author.name if author else ""

    @property
    def author_credentials(self) -> str:
        author = getattr(self, "primary_author", None)
        return getattr(author, "credentials", "") or ""

    @property
    def author_bio(self) -> str:
        author = getattr(self, "primary_author", None)
        return getattr(author, "bio", "") or ""

    @property
    def reading_time_minutes(self) -> int:
        return getattr(self, "reading_time", 0) or 0

    @property
    def thumbnail(self):
        return self.featured_image

    @property
    def category_name(self) -> str:
        cat = getattr(self, "category", None)
        return cat.name if cat else ""

    @property
    def tag_names(self) -> list[str]:
        return [t.name for t in self.tags.all()]

    @property
    def views_count(self) -> int:
        annotated = getattr(self, "engagement_views_count", None)
        if annotated is not None:
            return annotated
        if getattr(self, "_engagement_prefetched", False):
            cached = getattr(self, "_cached_engagement", None)
            return cached.total_views if cached is not None else 0
        cached = getattr(self, "_cached_engagement", None)
        if cached is not None:
            return cached.total_views
        from django.contrib.contenttypes.models import ContentType
        from cms_engagement.models import EngagementSummary
        try:
            ct = ContentType.objects.get_for_model(self.__class__)
            return EngagementSummary.objects.get(content_type=ct, object_id=self.pk).total_views
        except Exception:
            return 0

    @property
    def likes_count(self) -> int:
        annotated = getattr(self, "engagement_likes_count", None)
        if annotated is not None:
            return annotated
        if getattr(self, "_engagement_prefetched", False):
            cached = getattr(self, "_cached_engagement", None)
            return cached.thumbs_up_count if cached is not None else 0
        cached = getattr(self, "_cached_engagement", None)
        if cached is not None:
            return cached.thumbs_up_count
        from django.contrib.contenttypes.models import ContentType
        from cms_engagement.models import EngagementSummary
        try:
            ct = ContentType.objects.get_for_model(self.__class__)
            return EngagementSummary.objects.get(content_type=ct, object_id=self.pk).thumbs_up_count
        except Exception:
            return 0

    @property
    def page_content_type_id(self) -> int:
        from django.contrib.contenttypes.models import ContentType
        return ContentType.objects.get_for_model(self.__class__).pk

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    @property
    def frontend_url(self) -> str:
        """Flat canonical URL served by the Nuxt frontend (/:slug, no /blog/ prefix)."""
        site = self.get_site()
        root = site.root_url.rstrip("/") if site else ""
        return f"{root}/{self.slug}"

    @property
    def canonical_published_at(self):
        """The date to display and use in Schema.org as datePublished.

        Returns original_published_at if staff set it during a content
        migration; otherwise falls back to Wagtail's first_published_at.
        """
        return self.original_published_at or self.first_published_at

    @property
    def word_count(self):
        """Calculate word count from StreamField body."""
        from cms_core.validators import _count_words_in_streamfield

        return _count_words_in_streamfield(self.body)

    @property
    def reading_time(self):
        """Estimated reading time in minutes (integer). Frontend appends ' min read'."""
        wc = self.word_count
        if not wc:
            return None
        return max(1, round(wc / 250))

    @property
    def toc(self):
        """Auto-generated table of contents from heading blocks."""
        from cms_core.validators import generate_toc

        return generate_toc(self.body)

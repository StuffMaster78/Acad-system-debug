"""
CMS Content Graph
==================

The relational glue of the platform. Models how content connects
to form conversion funnels. Implements pillar/hub/spoke structure.

Core concept: Blog posts lead to service pages, which convert to orders.
The BlogServiceLink is the measurable conversion path between them.
The ContentPillar organizes content around services.

This is a pure Django app — no Wagtail Page types. Just Django models
and services that reference Wagtail pages via ForeignKeys.
"""

from django.db import models


class ContentPillar(models.Model):
    """A topical authority cluster organized around one service.

    Structure:
        ServicePage (the conversion destination)
        ├── Hub post (the flagship guide)
        └── Spoke posts (supporting content, linked via BlogPost.pillar FK)

    The pillar's health is measured by: spoke count, SERP coverage,
    internal linking density, and end-to-end funnel conversion.
    """

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="content_pillars",
    )
    name = models.CharField(
        max_length=255,
        help_text="e.g., 'Nursing Care Plans', 'APA Essay Writing'",
    )
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)

    # The funnel destination
    service_page = models.OneToOneField(
        "cms_service_pages.ServicePage",
        on_delete=models.CASCADE,
        related_name="pillar",
        help_text="The service page this pillar funnels traffic toward",
    )

    # The centerpiece guide
    hub_post = models.ForeignKey(
        "cms_blog.BlogPostPage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hubs_for",
        help_text="The flagship/comprehensive guide for this topic cluster",
    )

    # Target keywords for SERP tracking
    target_keywords = models.JSONField(
        default=list,
        blank=True,
        help_text='e.g., ["nursing care plan", "care plan template", "nursing care plan example"]',
    )

    # Computed metrics (refreshed nightly by cms_intelligence)
    spoke_count = models.PositiveIntegerField(default=0)
    avg_gsc_position = models.FloatField(default=0.0)
    total_clicks_30d = models.PositiveIntegerField(default=0)
    total_conversions_30d = models.PositiveIntegerField(default=0)
    attributed_revenue_30d = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["site", "slug"]
        ordering = ["-attributed_revenue_30d", "name"]

    def __str__(self):
        return f"{self.name} → {self.service_page.title}"

    @property
    def spoke_posts(self):
        """All blog posts in this pillar (excluding the hub)."""
        from cms_blog.models import BlogPostPage

        qs = BlogPostPage.objects.live().filter(pillar=self)
        if self.hub_post:
            qs = qs.exclude(id=self.hub_post.id)
        return qs


class BlogServiceLink(models.Model):
    """A measurable conversion path from a blog post to a service page.

    This is the platform's core mechanic. Each link has a placement,
    CTA text, and performance tracking.

    The composer renders these visibly. The intelligence layer measures
    each link's CTR and conversion attribution.
    """

    blog_post = models.ForeignKey(
        "cms_blog.BlogPostPage",
        on_delete=models.CASCADE,
        related_name="service_routes",
    )
    service_page = models.ForeignKey(
        "cms_service_pages.ServicePage",
        on_delete=models.CASCADE,
        related_name="blog_sources",
    )

    PLACEMENT_CHOICES = [
        ("inline_natural", "Inline natural link in body text"),
        ("inline_card", "Inline call-out card mid-article"),
        ("end_cta", "CTA block at end of post"),
        ("sidebar", "Sticky sidebar callout"),
        ("after_intro", "Soft mention after introduction"),
    ]
    placement = models.CharField(max_length=30, choices=PLACEMENT_CHOICES)

    cta_text = models.CharField(
        max_length=200,
        help_text=(
            "The pitch text for this specific route, e.g., "
            "'Need a custom care plan written by an RN? See our service →'"
        ),
    )
    is_primary_route = models.BooleanField(
        default=False,
        help_text="Is this the main conversion route for this blog post?",
    )

    # Performance tracking (updated nightly by cms_intelligence)
    impressions = models.PositiveIntegerField(
        default=0,
        help_text="Times this link was rendered on a page view",
    )
    clicks = models.PositiveIntegerField(
        default=0,
        help_text="Times this link was clicked",
    )
    attributed_conversions = models.PositiveIntegerField(
        default=0,
        help_text="Orders attributed to this link",
    )
    attributed_revenue = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["blog_post", "service_page"]),
            models.Index(fields=["service_page", "clicks"]),
        ]
        ordering = ["-is_primary_route", "-clicks"]

    def __str__(self):
        return f"{self.blog_post.title} → {self.service_page.title} ({self.placement})"

    @property
    def ctr(self):
        """Click-through rate."""
        if self.impressions == 0:
            return 0.0
        return (self.clicks / self.impressions) * 100


class ContentRelationship(models.Model):
    """Lateral relationship between two blog posts.

    Used for internal linking suggestions and the 'Related Posts' block.
    Lightweight — just type and strength. Not the over-elaborate
    semantic typing from earlier drafts.
    """

    RELATIONSHIP_TYPES = [
        ("related", "Related — same broad topic"),
        ("prerequisite", "Prerequisite — read this first"),
        ("deepdive", "Deep Dive — more detail on this aspect"),
        ("example", "Example — concrete instance of the concept"),
    ]

    from_post = models.ForeignKey(
        "cms_blog.BlogPostPage",
        on_delete=models.CASCADE,
        related_name="outgoing_relationships",
    )
    to_post = models.ForeignKey(
        "cms_blog.BlogPostPage",
        on_delete=models.CASCADE,
        related_name="incoming_relationships",
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES,
        default="related",
    )
    strength = models.FloatField(
        default=0.7,
        help_text="0.0 to 1.0 — how relevant is this link?",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["from_post", "to_post"]
        ordering = ["-strength"]

    def __str__(self):
        return f"{self.from_post.title} —[{self.relationship_type}]→ {self.to_post.title}"
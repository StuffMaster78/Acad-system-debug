"""
Content Graph Admin
=====================

Admin views for managing funnels, pillars, and content relationships.
"""

from django.contrib import admin
from django.utils.html import format_html

from cms_content_graph.models import (
    BlogServiceLink,
    ContentPillar,
    ContentRelationship,
)


@admin.register(ContentPillar)
class ContentPillarAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "site",
        "service_page_title",
        "hub_post_title",
        "spoke_count",
        "total_clicks_30d",
        "total_conversions_30d",
        "attributed_revenue_30d",
    ]
    list_filter = ["site"]
    search_fields = ["name", "description"]
    readonly_fields = [
        "spoke_count",
        "avg_gsc_position",
        "total_clicks_30d",
        "total_conversions_30d",
        "attributed_revenue_30d",
    ]
    raw_id_fields = ["service_page", "hub_post"]

    def service_page_title(self, obj):
        return obj.service_page.title if obj.service_page else "—"

    service_page_title.short_description = "Service Page"

    def hub_post_title(self, obj):
        return obj.hub_post.title if obj.hub_post else "—"

    hub_post_title.short_description = "Hub Post"


@admin.register(BlogServiceLink)
class BlogServiceLinkAdmin(admin.ModelAdmin):
    list_display = [
        "blog_post_title",
        "service_page_title",
        "placement",
        "is_primary_route",
        "clicks",
        "impressions",
        "display_ctr",
        "attributed_conversions",
        "attributed_revenue",
    ]
    list_filter = [
        "placement",
        "is_primary_route",
        "service_page",
    ]
    search_fields = [
        "blog_post__title",
        "service_page__title",
        "cta_text",
    ]
    raw_id_fields = ["blog_post", "service_page"]
    readonly_fields = [
        "impressions",
        "clicks",
        "attributed_conversions",
        "attributed_revenue",
    ]

    def blog_post_title(self, obj):
        return obj.blog_post.title

    blog_post_title.short_description = "Blog Post"

    def service_page_title(self, obj):
        return obj.service_page.title

    service_page_title.short_description = "Service Page"

    def display_ctr(self, obj):
        ctr = obj.ctr
        color = "#28a745" if ctr > 5 else "#ffc107" if ctr > 2 else "#dc3545"
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            ctr,
        )

    display_ctr.short_description = "CTR"


@admin.register(ContentRelationship)
class ContentRelationshipAdmin(admin.ModelAdmin):
    list_display = [
        "from_post_title",
        "relationship_type",
        "to_post_title",
        "strength",
    ]
    list_filter = ["relationship_type"]
    raw_id_fields = ["from_post", "to_post"]

    def from_post_title(self, obj):
        return obj.from_post.title

    from_post_title.short_description = "From"

    def to_post_title(self, obj):
        return obj.to_post.title

    to_post_title.short_description = "To"
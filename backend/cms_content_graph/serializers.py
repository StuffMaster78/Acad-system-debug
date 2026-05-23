"""
Content Graph API Serializers
================================
"""

from rest_framework import serializers

from cms_content_graph.models import (
    BlogServiceLink,
    ContentPillar,
    ContentRelationship,
)


class ContentPillarSerializer(serializers.ModelSerializer):
    service_page_title = serializers.CharField(
        source="service_page.title", read_only=True
    )
    service_page_url = serializers.CharField(
        source="service_page.url", read_only=True
    )
    hub_post_title = serializers.SerializerMethodField()
    hub_post_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentPillar
        fields = [
            "id", "name", "slug", "description",
            "service_page_title", "service_page_url",
            "hub_post_title", "hub_post_url",
            "target_keywords",
            "spoke_count", "avg_gsc_position",
            "total_clicks_30d", "total_conversions_30d",
            "attributed_revenue_30d",
        ]

    def get_hub_post_title(self, obj) -> str | None:
        return obj.hub_post.title if obj.hub_post else None

    def get_hub_post_url(self, obj) -> str | None:
        return obj.hub_post.url if obj.hub_post else None


class BlogServiceLinkSerializer(serializers.ModelSerializer):
    blog_post_title = serializers.CharField(
        source="blog_post.title", read_only=True
    )
    service_page_title = serializers.CharField(
        source="service_page.title", read_only=True
    )
    ctr = serializers.FloatField(read_only=True)

    class Meta:
        model = BlogServiceLink
        fields = [
            "id", "blog_post", "blog_post_title",
            "service_page", "service_page_title",
            "placement", "cta_text", "is_primary_route",
            "impressions", "clicks", "ctr",
            "attributed_conversions", "attributed_revenue",
        ]


class ContentRelationshipSerializer(serializers.ModelSerializer):
    from_post_title = serializers.CharField(
        source="from_post.title", read_only=True
    )
    to_post_title = serializers.CharField(
        source="to_post.title", read_only=True
    )

    class Meta:
        model = ContentRelationship
        fields = [
            "id", "from_post", "from_post_title",
            "to_post", "to_post_title",
            "relationship_type", "strength",
        ]
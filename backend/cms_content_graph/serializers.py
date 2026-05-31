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
    service_page = serializers.SerializerMethodField()
    hub_post = serializers.SerializerMethodField()

    class Meta:
        model = ContentPillar
        fields = [
            "id", "name", "slug", "description",
            "service_page", "hub_post",
            "target_keywords",
            "spoke_count", "avg_gsc_position",
            "total_clicks_30d", "total_conversions_30d",
            "attributed_revenue_30d",
        ]

    def get_service_page(self, obj) -> dict | None:
        sp = obj.service_page
        if not sp:
            return None
        return {"id": sp.pk, "title": sp.title, "slug": sp.slug}

    def get_hub_post(self, obj) -> dict | None:
        hp = obj.hub_post
        if not hp:
            return None
        return {"id": hp.pk, "title": hp.title, "slug": hp.slug}


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
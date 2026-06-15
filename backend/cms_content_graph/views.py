"""
Content Graph API Views
=========================

Endpoints for pillars, blog-service links, funnel analytics,
and internal linking suggestions.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from authentication.permissions import IsAdminOrSuperAdmin

from cms_content_graph.models import (
    BlogServiceLink,
    ContentPillar,
    ContentRelationship,
)
from cms_content_graph.serializers import (
    BlogServiceLinkSerializer,
    ContentPillarSerializer,
    ContentRelationshipSerializer,
)


class ContentPillarViewSet(viewsets.ReadOnlyModelViewSet):
    """Pillar API — read-only public, with funnel analytics."""

    serializer_class = ContentPillarSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        site = getattr(self.request, "site", None)
        qs = ContentPillar.objects.select_related("service_page", "hub_post")
        if site:
            qs = qs.filter(site=site)
        return qs

    @action(detail=True, methods=["get"])
    def funnel(self, request, slug=None):
        """GET /cms-api/content-graph/pillars/{slug}/funnel/"""
        pillar = self.get_object()
        try:
            from cms_intelligence.services.funnel_analytics import FunnelAnalyticsService

            report = FunnelAnalyticsService.get_funnel_report(pillar)
            return Response(report)
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def spokes(self, request, slug=None):
        """GET /cms-api/content-graph/pillars/{slug}/spokes/ — spoke posts."""
        pillar = self.get_object()
        from cms_blog.serializers import BlogPostListSerializer

        posts = pillar.spoke_posts.order_by("-first_published_at")[:50]
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)


class BlogServiceLinkViewSet(viewsets.ModelViewSet):
    """Blog→Service link management. Admin-only write, public read."""

    serializer_class = BlogServiceLinkSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminOrSuperAdmin()]

    def get_queryset(self):
        qs = BlogServiceLink.objects.select_related(
            "blog_post", "service_page"
        )
        # Filter by blog post or service page
        blog_id = self.request.query_params.get("blog_post")
        service_id = self.request.query_params.get("service_page")
        if blog_id:
            qs = qs.filter(blog_post_id=blog_id)
        if service_id:
            qs = qs.filter(service_page_id=service_id)
        return qs


class LinkSuggestionView(viewsets.ViewSet):
    """GET /cms-api/content-graph/suggest/?page_id=123
    Returns internal link suggestions for a page."""

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        page_id = request.query_params.get("page_id")
        if not page_id:
            return Response(
                {"error": "page_id parameter required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from wagtail.models import Page

            page = Page.objects.get(pk=page_id).specific
        except Exception:
            return Response(
                {"error": "Page not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        from cms_content_graph.services.linking_service import InternalLinkingService

        suggestions = InternalLinkingService.suggest_links_for_page(page)
        return Response(suggestions)
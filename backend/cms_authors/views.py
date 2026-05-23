"""
Author API Views
==================

Read-only API for public author profiles.
Write operations happen through Wagtail admin.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from cms_authors.models import Author
from cms_authors.serializers import AuthorSerializer, AuthorMinimalSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """Public author API — read-only, filtered by site."""

    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        site = getattr(self.request, "site", None)
        qs = Author.objects.filter(is_active=True, show_publicly=True)
        if site:
            qs = qs.filter(site=site)
        return qs.select_related("site")

    @action(detail=True, methods=["get"])
    def posts(self, request, slug=None):
        """GET /cms-api/authors/{slug}/posts/ — author's published posts."""
        author = self.get_object()
        try:
            from cms_blog.models import BlogPostPage
            from cms_blog.serializers import BlogPostListSerializer

            posts = (
                BlogPostPage.objects.live()
                .filter(primary_author=author)
                .order_by("-first_published_at")[:20]
            )
            serializer = BlogPostListSerializer(posts, many=True)
            return Response(serializer.data)
        except ImportError:
            return Response([])
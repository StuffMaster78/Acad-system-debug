"""
Reference API Views
=====================

CRUD for references, citations, and DOI/PMID resolution.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from cms_core.services.tenant_service import filter_queryset_by_user_sites
from cms_references.models import Citation, Reference
from cms_references.serializers import (
    CitationCreateSerializer,
    CitationSerializer,
    ReferenceCreateSerializer,
    ReferenceSerializer,
)


class ReferenceViewSet(viewsets.ModelViewSet):
    """Reference library API. Authenticated users can CRUD."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ReferenceCreateSerializer
        return ReferenceSerializer

    def get_queryset(self):
        qs = Reference.objects.prefetch_related("tags")
        return filter_queryset_by_user_sites(qs, self.request.user)

    @action(detail=False, methods=["post"])
    def resolve_doi(self, request):
        """POST /cms-api/references/resolve_doi/ {"doi": "10.1234/..."}
        Auto-fills reference fields from Crossref."""
        doi = request.data.get("doi", "").strip()
        if not doi:
            return Response(
                {"error": "doi field required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from cms_references.services.resolvers import DOIResolver

        result = DOIResolver.resolve(doi)
        if result:
            return Response(result)
        return Response(
            {"error": "Could not resolve DOI"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @action(detail=False, methods=["post"])
    def resolve_pmid(self, request):
        """POST /cms-api/references/resolve_pmid/ {"pmid": "12345678"}
        Auto-fills reference fields from PubMed."""
        pmid = request.data.get("pmid", "").strip()
        if not pmid:
            return Response(
                {"error": "pmid field required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from cms_references.services.resolvers import PMIDResolver

        result = PMIDResolver.resolve(pmid)
        if result:
            return Response(result)
        return Response(
            {"error": "Could not resolve PMID"},
            status=status.HTTP_404_NOT_FOUND,
        )


class CitationViewSet(viewsets.ModelViewSet):
    """Citation management — link references to blog posts."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CitationCreateSerializer
        return CitationSerializer

    def get_queryset(self):
        qs = Citation.objects.select_related("reference", "blog_post")
        blog_post_id = self.request.query_params.get("blog_post")
        if blog_post_id:
            qs = qs.filter(blog_post_id=blog_post_id)
        return qs

class CitationDensityView(viewsets.ViewSet):
    """
    GET /cms-api/references/citation-density/
    Admin view — blog posts annotated with citation counts.
    Returns all live blog posts ordered by citation count ascending
    so editors see zero-citation posts first.

    Filters:
      needs_citations=true  Only posts where citation_mode != 'none' and count=0
      min_count=N           Only posts with N or more citations
    """

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def density(self, request):
        from django.db.models import Count, Q
        from wagtail.models import Site as WagtailSite

        try:
            from cms_blog.models import BlogPostPage
        except ImportError:
            return Response({"error": "BlogPostPage not available."}, status=400)

        # Resolve Wagtail site for tenant scoping
        site_ids = []
        try:
            for s in WagtailSite.objects.all():
                site_ids.append(s.id)
        except Exception:
            pass

        qs = (
            BlogPostPage.objects.live()
            .annotate(citation_count=Count("citations", distinct=True))
            .select_related("owner", "locale")
            .order_by("citation_count", "title")
        )

        if site_ids:
            qs = qs.filter(get_site__site_id__in=site_ids) if hasattr(BlogPostPage, "get_site") else qs

        # Filter: only posts that should have citations but don't
        needs_citations = request.query_params.get("needs_citations")
        if needs_citations and needs_citations.lower() == "true":
            qs = qs.filter(citation_count=0).exclude(citation_mode="none")

        min_count = request.query_params.get("min_count")
        if min_count:
            try:
                qs = qs.filter(citation_count__gte=int(min_count))
            except ValueError:
                pass

        results = []
        for post in qs[:200]:  # cap at 200 for performance
            results.append({
                "id":            post.id,
                "title":         post.title,
                "slug":          post.slug,
                "url_path":      post.url_path,
                "citation_mode": post.citation_mode,
                "citation_count": post.citation_count,
                "needs_citations": post.citation_mode != "none" and post.citation_count == 0,
                "first_published_at": post.first_published_at.isoformat() if post.first_published_at else None,
                "last_published_at":  post.last_published_at.isoformat() if post.last_published_at else None,
                "wagtail_edit_url": f"/cms-admin/pages/{post.id}/edit/",
            })

        total  = BlogPostPage.objects.live().count()
        with_cit  = BlogPostPage.objects.live().filter(
            id__in=Citation.objects.values("blog_post_id").distinct()
        ).count()
        needs_cit = BlogPostPage.objects.live().exclude(
            citation_mode="none"
        ).filter(citation_count=0).annotate(
            citation_count=Count("citations", distinct=True)
        ).count()

        return Response({
            "summary": {
                "total_posts":         total,
                "posts_with_citations": with_cit,
                "posts_needing_citations": needs_cit,
                "coverage_pct": round(with_cit / total * 100, 1) if total else 0,
            },
            "posts": results,
        })

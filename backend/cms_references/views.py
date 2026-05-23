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
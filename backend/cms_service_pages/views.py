from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from cms_core.services.tenant_service import get_current_site
from cms_service_pages.models import ServicePage
from cms_service_pages.serializers import (
    ServicePageDetailSerializer,
    ServicePageListSerializer,
)


def _tenant_service_queryset(request):
    qs = (
        ServicePage.objects.live()
        .public()
        .select_related("service_category", "reviewer")
        .order_by("title")
    )
    site = get_current_site(request)
    if site and getattr(site, "root_page", None):
        qs = qs.descendant_of(site.root_page)
    return qs


class ServicePageListView(APIView):
    """GET /cms-api/service-pages/"""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        pages = _tenant_service_queryset(request)
        category = request.query_params.get("category")
        if category:
            pages = pages.filter(service_category__slug=category)

        serializer = ServicePageListSerializer(pages, many=True)
        return Response({"results": serializer.data})


class ServicePageBySlugView(APIView):
    """GET /cms-api/service-pages/by-slug/<slug>/"""

    permission_classes = [permissions.AllowAny]

    def get(self, request, slug: str):
        try:
            page = _tenant_service_queryset(request).get(slug=slug)
        except ServicePage.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        serializer = ServicePageDetailSerializer(page)
        return Response(serializer.data)


class ServicePageSchemaView(APIView):
    """GET /cms-api/service-pages/schema/<page_id>/"""

    permission_classes = [permissions.AllowAny]

    def get(self, request, page_id):
        from wagtail.models import Page

        try:
            page = Page.objects.live().get(pk=page_id).specific
        except Page.DoesNotExist:
            return Response({"error": "Page not found"}, status=404)

        from cms_service_pages.serializers import ServicePageSchemaOrgSerializer

        schema = ServicePageSchemaOrgSerializer().to_representation(page)
        return Response(schema)

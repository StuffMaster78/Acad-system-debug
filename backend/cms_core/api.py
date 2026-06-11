"""
Wagtail API v2 Configuration
==============================

Exposes pages, images, and documents as JSON endpoints
for the Vue/Nuxt frontends to consume.

Endpoints:
    /api/v2/pages/ — all published pages (filterable by type, site)
    /api/v2/images/ — all images
    /api/v2/documents/ — all documents

Usage in frontend:
    GET /api/v2/pages/?type=cms_blog.BlogPostPage&fields=*
    GET /api/v2/pages/?type=cms_service_pages.ServicePage&fields=*
    GET /api/v2/pages/<id>/?fields=body,primary_author,category,...
"""

from rest_framework.permissions import AllowAny

from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet


class TenantFilteredPagesAPIViewSet(PagesAPIViewSet):
    """Extend the default pages API to support site-based filtering.

    Usage:
        GET /api/v2/pages/?site=<site_id>
        GET /api/v2/pages/?site=<site_id>&type=cms_blog.BlogPostPage
    """

    # Public read — Wagtail pages contain no sensitive data.
    # Sensitive business data lives in the DRF API, not the page tree.
    permission_classes = [AllowAny]

    # Additional fields that can be used for filtering
    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(
        {"site"}
    )

    def get_queryset(self):
        qs = super().get_queryset()
        site_id = self.request.query_params.get("site")
        if site_id:
            from wagtail.models import Site

            try:
                site = Site.objects.get(id=site_id)
                # Filter to pages that are descendants of this site's root page
                qs = qs.descendant_of(site.root_page, inclusive=True)
            except Site.DoesNotExist:
                qs = qs.none()
        return qs


# Create the router and register endpoints
api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", TenantFilteredPagesAPIViewSet)
api_router.register_endpoint("images", ImagesAPIViewSet)
api_router.register_endpoint("documents", DocumentsAPIViewSet)
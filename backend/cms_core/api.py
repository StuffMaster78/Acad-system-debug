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

from django.contrib.contenttypes.models import ContentType
from django.db.models import IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
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

        # BlogPostPage exposes materialized engagement counters as API fields.
        # Annotate them in the listing query so requesting fields=* does not
        # execute two EngagementSummary lookups for every article.
        from cms_blog.models import BlogPostPage

        if qs.model is BlogPostPage:
            from cms_engagement.models import EngagementSummary

            content_type_id = ContentType.objects.get_for_model(BlogPostPage).pk
            summaries = EngagementSummary.objects.filter(
                content_type_id=content_type_id,
                object_id=OuterRef("pk"),
            )
            qs = qs.annotate(
                engagement_views_count=Coalesce(
                    Subquery(summaries.values("total_views")[:1]),
                    Value(0),
                    output_field=IntegerField(),
                ),
                engagement_likes_count=Coalesce(
                    Subquery(summaries.values("thumbs_up_count")[:1]),
                    Value(0),
                    output_field=IntegerField(),
                ),
            )

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

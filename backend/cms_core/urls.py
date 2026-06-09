"""
CMS URL Configuration
=======================

Main router that includes all CMS app URLs.

Add to your project's urls.py::

    urlpatterns = [
        ...
        path("cms-api/", include("cms_core.urls")),
        ...
    ]

Wagtail's own API (pages, images, documents) is served separately
via the api_router in cms_core/api.py::

    path("api/v2/", api_router.urls),
"""

from django.urls import include, path
from cms_core.views import ContentHealthView, CreatePageDraftView

app_name = "cms"

urlpatterns = [
    path("content-health/", ContentHealthView.as_view(), name="content-health"),
    path("pages/create-draft/", CreatePageDraftView.as_view(), name="create-page-draft"),
    path("content-graph/", include("cms_content_graph.urls")),
    path("references/", include("cms_references.urls")),
    path("attachments/", include("cms_attachments.urls")),
    path("engagement/", include("cms_engagement.urls")),
    path("intelligence/", include("cms_intelligence.urls")),
    path("newsletters/", include("cms_newsletters.urls")),
    path("files/", include("files_management.urls")),
    path("authors/", include("cms_authors.urls")),
    path("blog/", include("cms_blog.urls")),
]
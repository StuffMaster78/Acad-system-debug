from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms_content_graph.views import (
    BlogServiceLinkViewSet,
    ContentPillarViewSet,
    LinkSuggestionView,
)

router = DefaultRouter()
router.register("pillars", ContentPillarViewSet, basename="pillar")
router.register("links", BlogServiceLinkViewSet, basename="blog-service-link")
router.register("suggest", LinkSuggestionView, basename="link-suggestions")

app_name = "cms_content_graph"

urlpatterns = [
    path("", include(router.urls)),
]
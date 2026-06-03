from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms_references.views import CitationViewSet, CitationDensityView, ReferenceViewSet

router = DefaultRouter()
router.register("library",          ReferenceViewSet,    basename="reference")
router.register("citations",        CitationViewSet,     basename="citation")
router.register("citation-density", CitationDensityView, basename="citation-density")

app_name = "cms_references"

urlpatterns = [
    path("", include(router.urls)),
]

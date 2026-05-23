from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms_authors.views import AuthorViewSet

router = DefaultRouter()
router.register("", AuthorViewSet, basename="author")

app_name = "cms_authors"

urlpatterns = [
    path("", include(router.urls)),
]
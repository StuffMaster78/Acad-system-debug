from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms_attachments.views import AttachmentViewSet

router = DefaultRouter()
router.register("", AttachmentViewSet, basename="attachment")

app_name = "cms_attachments"

urlpatterns = [
    path("", include(router.urls)),
]
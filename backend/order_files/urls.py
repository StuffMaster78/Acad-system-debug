from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderFileViewSet,
    FileDeletionRequestViewSet,
    ExternalFileLinkViewSet,
    ExtraServiceFileViewSet,
    OrderFilesConfigViewSet,
    OrderFileCategoryViewSet,
    FileDownloadLogViewSet,
    StyleReferenceFileViewSet,
)

router = DefaultRouter()
router.register(r"order-files", OrderFileViewSet)
router.register(r"file-deletion-requests", FileDeletionRequestViewSet)
router.register(r"external-links", ExternalFileLinkViewSet)
router.register(r"extra-service-files", ExtraServiceFileViewSet)
router.register(r"order-files-config", OrderFilesConfigViewSet, basename="order-files-config")
router.register(r"file-categories", OrderFileCategoryViewSet, basename="file-categories")
router.register(r"download-logs", FileDownloadLogViewSet, basename="download-log")
router.register(r"style-reference-files", StyleReferenceFileViewSet, basename="style-reference-file")

urlpatterns = [
    path("", include(router.urls)),
]
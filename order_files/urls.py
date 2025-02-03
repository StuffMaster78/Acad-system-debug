from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderFileViewSet, FileDeletionRequestViewSet, ExternalFileLinkViewSet, ExtraServiceFileViewSet, OrderFilesConfigViewSet
)

router = DefaultRouter()
router.register(r"order-files", OrderFileViewSet)
router.register(r"file-deletion-requests", FileDeletionRequestViewSet)
router.register(r"external-links", ExternalFileLinkViewSet)
router.register(r"extra-service-files", ExtraServiceFileViewSet)
router.register(r"order-files-config", OrderFilesConfigViewSet, basename="order-files-config")

urlpatterns = [
    path("", include(router.urls)),
]
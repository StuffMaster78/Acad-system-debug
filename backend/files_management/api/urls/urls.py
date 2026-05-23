from django.urls import include, path
from rest_framework.routers import DefaultRouter
from files_management.api.views.views import (
    FileAttachView,
    FileDeletionRequestView,
    FileDownloadView,
    FileUploadView,
)
from files_management.api.views.views import FileQuotaView, ManagedFileViewSet

router = DefaultRouter()

router.register("managed", ManagedFileViewSet, basename="managed-file")
router.register("quota", FileQuotaView, basename="file-quota")

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("attach/", FileAttachView.as_view(), name="file-attach"),
    path(
        "download/<int:attachment_id>/",
        FileDownloadView.as_view(),
        name="file-download",
    ),
    path(
        "deletion/request/",
        FileDeletionRequestView.as_view(),
        name="file-deletion-request",
    ),
]
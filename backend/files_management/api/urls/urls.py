from django.urls import path

from files_management.api.views.views import (
    FileAttachView,
    FileDeletionRequestView,
    FileDownloadView,
    FileUploadView,
)

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
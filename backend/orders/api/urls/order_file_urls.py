from django.urls import path

from orders.api.views.files.order_file_views import (
    OrderClientMaterialFileUploadView,
    OrderDraftFileUploadView,
    OrderExtraServiceFileUploadView,
    OrderExternalFileLinkView,
    OrderFileDeletionRequestView,
    OrderFileDownloadView,
    OrderFileListView,
    OrderFinalFileUploadView,
    OrderInstructionFileUploadView,
    OrderInternalFileUploadView,
    OrderReferenceFileUploadView,
    OrderRevisionFileUploadView,
    OrderStyleReferenceFileUploadView,
    OrderSubmitFinalView,
    OrderWriterGuideFileUploadView,
)

urlpatterns = [
    path(
        "<int:order_id>/files/",
        OrderFileListView.as_view(),
        name="order-file-list",
    ),
    # ── Client materials ──────────────────────────────────────────────────
    path(
        "<int:order_id>/files/instructions/",
        OrderInstructionFileUploadView.as_view(),
        name="order-file-upload-instruction",
    ),
    path(
        "<int:order_id>/files/references/",
        OrderReferenceFileUploadView.as_view(),
        name="order-file-upload-reference",
    ),
    path(
        "<int:order_id>/files/style-references/",
        OrderStyleReferenceFileUploadView.as_view(),
        name="order-file-upload-style-reference",
    ),
    # Generic client material types (samples, outlines, questionnaires, notes, class-materials)
    path(
        "<int:order_id>/files/<str:material_type>/",
        OrderClientMaterialFileUploadView.as_view(),
        name="order-file-upload-client-material",
    ),
    # ── Writer deliverables ───────────────────────────────────────────────
    path(
        "<int:order_id>/files/drafts/",
        OrderDraftFileUploadView.as_view(),
        name="order-file-upload-draft",
    ),
    path(
        "<int:order_id>/files/final/",
        OrderFinalFileUploadView.as_view(),
        name="order-file-upload-final",
    ),
    path(
        "<int:order_id>/files/revisions/",
        OrderRevisionFileUploadView.as_view(),
        name="order-file-upload-revision",
    ),
    path(
        "<int:order_id>/files/extra-services/",
        OrderExtraServiceFileUploadView.as_view(),
        name="order-file-upload-extra-service",
    ),
    # ── Staff uploads ─────────────────────────────────────────────────────
    path(
        "<int:order_id>/files/writer-guides/",
        OrderWriterGuideFileUploadView.as_view(),
        name="order-file-upload-writer-guide",
    ),
    path(
        "<int:order_id>/files/internal/",
        OrderInternalFileUploadView.as_view(),
        name="order-file-upload-internal",
    ),
    # ── External links ────────────────────────────────────────────────────
    path(
        "<int:order_id>/files/external-links/",
        OrderExternalFileLinkView.as_view(),
        name="order-file-external-link",
    ),
    # ── Per-attachment actions ────────────────────────────────────────────
    path(
        "<int:order_id>/files/<int:attachment_id>/download/",
        OrderFileDownloadView.as_view(),
        name="order-file-download",
    ),
    path(
        "<int:order_id>/files/<int:attachment_id>/submit-final/",
        OrderSubmitFinalView.as_view(),
        name="order-file-submit-final",
    ),
    path(
        "<int:order_id>/files/<int:attachment_id>/request-deletion/",
        OrderFileDeletionRequestView.as_view(),
        name="order-file-request-deletion",
    ),
]

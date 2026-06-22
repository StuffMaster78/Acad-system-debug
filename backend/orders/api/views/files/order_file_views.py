from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from files_management.exceptions import FileManagementError
from files_management.enums import FilePurpose, FileVisibility
from files_management.models.file_download_receipt import FileDownloadReceipt
from files_management.selectors import FileAttachmentSelector
from files_management.services import FileDeletionService
from orders.api.serializers.files.order_file_serializers import (
    OrderExternalFileLinkSerializer,
    OrderExtraServiceFileUploadSerializer,
    OrderFileAttachmentSerializer,
    OrderFileDeletionRequestSerializer,
    OrderFileUploadSerializer,
    OrderStyleReferenceUploadSerializer,
)
from orders.models import Order
from orders.services.order_file_download_service import (
    OrderFileDownloadService,
)
from orders.services.order_file_service import OrderFileService


class OrderFileBaseView(APIView):
    """
    Base helpers for order file endpoints.
    """

    permission_classes = [IsAuthenticated]

    def get_order(self, request, order_id: int) -> Order:
        """
        Return an order scoped to the authenticated user's website.
        Superadmins and superusers bypass website scoping.
        """
        user = request.user
        if user.is_superuser or getattr(user, 'role', None) == 'superadmin':
            return get_object_or_404(Order, id=order_id)
        return get_object_or_404(
            Order,
            id=order_id,
            website=user.website,
        )

    def ensure_client_or_staff(self, *, order, user) -> None:
        """
        Ensure user is order client or staff.
        """

        if self.is_staff(user=user):
            return

        if self.is_order_client(order=order, user=user):
            return

        raise PermissionDenied("You cannot upload files to this order.")

    def ensure_writer_or_staff(self, *, order, user) -> None:
        """
        Ensure user is assigned writer or staff.
        """

        if self.is_staff(user=user):
            return

        if self.is_order_writer(order=order, user=user):
            return

        raise PermissionDenied("You cannot upload writer files here.")

    @staticmethod
    def is_staff(*, user) -> bool:
        """
        Return whether the user is staff-like.
        """

        return bool(
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
            or getattr(user, "is_super_admin", False)
            or getattr(user, "role", None) in {"admin", "superadmin", "support", "editor"}
        )

    @staticmethod
    def is_order_client(*, order, user) -> bool:
        """
        Return whether user is the order client.
        """

        user_id = getattr(user, "id", None)

        for attr_name in ("client_id", "created_by_id"):
            if getattr(order, attr_name, None) == user_id:
                return True

        client = getattr(order, "client", None)

        if getattr(client, "user_id", None) == user_id:
            return True

        return getattr(client, "id", None) == user_id

    @staticmethod
    def is_order_writer(*, order, user) -> bool:
        """
        Return whether user is assigned writer.
        """

        user_id = getattr(user, "id", None)

        for attr_name in ("writer_id", "assigned_writer_id", "assigned_to_id"):
            if getattr(order, attr_name, None) == user_id:
                return True

        writer = getattr(order, "writer", None)
        assigned_writer = getattr(order, "assigned_writer", None)

        if getattr(writer, "user_id", None) == user_id:
            return True

        if getattr(assigned_writer, "user_id", None) == user_id:
            return True

        account_profile = getattr(assigned_writer, "account_profile", None)
        if getattr(account_profile, "user_id", None) == user_id:
            return True

        return False

    @staticmethod
    def handle_file_error(exc: FileManagementError) -> ValidationError:
        return ValidationError({"file": str(exc)})


class OrderFileListView(OrderFileBaseView):
    """
    List files attached to an order.
    """

    def get(self, request, order_id: int):
        order = self.get_order(request, order_id)

        attachments = FileAttachmentSelector.for_object(
            website=order.website,
            obj=order,
        ).select_related(
            "managed_file",
            "external_link",
            "attached_by",
        )

        if self.is_order_client(order=order, user=request.user) and not self.is_staff(user=request.user):
            attachments = attachments.exclude(
                purpose=FilePurpose.WRITER_GUIDE,
            ).exclude(
                visibility=FileVisibility.WRITER_AND_STAFF,
            ).exclude(
                visibility=FileVisibility.STAFF_ONLY,
            ).exclude(
                visibility=FileVisibility.INTERNAL_ONLY,
            )
        elif self.is_order_writer(order=order, user=request.user) and not self.is_staff(user=request.user):
            attachments = attachments.exclude(
                visibility=FileVisibility.CLIENT_AND_STAFF,
            ).exclude(
                visibility=FileVisibility.STAFF_ONLY,
            ).exclude(
                visibility=FileVisibility.INTERNAL_ONLY,
            )

        # Prefetch per-user download receipts in one query so the serializer
        # can compute is_new_for_user without an extra hit per file.
        attachment_list = list(attachments)
        if request.user.is_authenticated and attachment_list:
            downloaded_ids = set(
                FileDownloadReceipt.objects.filter(
                    attachment_id__in=[a.id for a in attachment_list],
                    user=request.user,
                ).values_list("attachment_id", flat=True)
            )
        else:
            downloaded_ids = set()

        return Response(
            OrderFileAttachmentSerializer(
                attachment_list,
                many=True,
                context={"request": request, "downloaded_attachment_ids": downloaded_ids},
            ).data
        )


class OrderInstructionFileUploadView(OrderFileBaseView):
    """
    Upload order instruction file.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)
        self.ensure_client_or_staff(order=order, user=request.user)

        serializer = OrderFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.client_upload_instruction(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderReferenceFileUploadView(OrderFileBaseView):
    """
    Upload order reference file.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)
        self.ensure_client_or_staff(order=order, user=request.user)

        serializer = OrderFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.client_upload_reference(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderStyleReferenceFileUploadView(OrderFileBaseView):
    """
    Upload a style reference file such as a previous paper or style guide.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)
        self.ensure_client_or_staff(order=order, user=request.user)

        serializer = OrderStyleReferenceUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.client_upload_style_reference(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
                reference_type=serializer.validated_data.get(
                    "reference_type",
                    "previous_paper",
                ),
                description=serializer.validated_data.get("description", ""),
                is_visible_to_writer=serializer.validated_data.get(
                    "is_visible_to_writer",
                    True,
                ),
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderExtraServiceFileUploadView(OrderFileBaseView):
    """
    Upload an extra service file such as a plagiarism report.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)
        self.ensure_writer_or_staff(order=order, user=request.user)

        serializer = OrderExtraServiceFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.writer_upload_extra_service(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
                service_code=serializer.validated_data.get("service_code", ""),
                category_code=serializer.validated_data.get("category_code", ""),
                description=serializer.validated_data.get("description", ""),
                is_downloadable=serializer.validated_data.get(
                    "is_downloadable",
                    False,
                ),
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDraftFileUploadView(OrderFileBaseView):
    """
    Upload writer draft file.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)
        self.ensure_writer_or_staff(order=order, user=request.user)

        serializer = OrderFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.writer_upload_draft(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderFinalFileUploadView(OrderFileBaseView):
    """
    Upload final order deliverable.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)
        self.ensure_writer_or_staff(order=order, user=request.user)

        serializer = OrderFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.writer_upload_final(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderRevisionFileUploadView(OrderFileBaseView):
    """
    Upload order revision file.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)
        self.ensure_writer_or_staff(order=order, user=request.user)

        serializer = OrderFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.writer_upload_revision(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderWriterGuideFileUploadView(OrderFileBaseView):
    """
    Upload staff-provided guide/resource files for writers.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)
        if not self.is_staff(user=request.user):
            raise PermissionDenied("Only staff can add writer guides.")

        serializer = OrderFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.staff_upload_writer_guide(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
                guide_type=serializer.validated_data.get("category_code", "guide"),
                description=serializer.validated_data.get("description", ""),
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderExternalFileLinkView(OrderFileBaseView):
    """
    Submit external file link for an order.
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)

        serializer = OrderExternalFileLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (
            serializer.validated_data["purpose"] == FilePurpose.WRITER_GUIDE
            and not self.is_staff(user=request.user)
        ):
            raise PermissionDenied("Only staff can add writer guide links.")

        try:
            attachment = OrderFileService.submit_external_link(
                order=order,
                submitted_by=request.user,
                url=serializer.validated_data["url"],
                purpose=serializer.validated_data["purpose"],
                title=serializer.validated_data.get("title", ""),
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderFileDownloadView(OrderFileBaseView):
    """
    Download an order file through order business rules.
    """

    def get(self, request, order_id: int, attachment_id: int):
        order = self.get_order(request, order_id)

        attachment = get_object_or_404(
            FileAttachmentSelector.for_object(
                website=order.website,
                obj=order,
            ),
            id=attachment_id,
        )

        try:
            url = OrderFileDownloadService.get_download_url(
                order=order,
                user=request.user,
                attachment=attachment,
                ip_address=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response({"url": url})


class OrderFileDeletionRequestView(OrderFileBaseView):
    """
    Request deletion of an order file.
    """

    def post(self, request, order_id: int, attachment_id: int):
        order = self.get_order(request, order_id)

        attachment = get_object_or_404(
            FileAttachmentSelector.for_object(
                website=order.website,
                obj=order,
            ),
            id=attachment_id,
        )

        serializer = OrderFileDeletionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deletion_request = FileDeletionService.request_deletion(
            website=order.website,
            requested_by=request.user,
            attachment=attachment,
            reason=serializer.validated_data["reason"],
            scope=serializer.validated_data.get("scope", "detach_only"),
        )

        return Response(
            {
                "id": deletion_request.id,
                "status": deletion_request.status,
            },
            status=status.HTTP_201_CREATED,
        )


# ── New client material types ─────────────────────────────────────────────────

_CLIENT_MATERIAL_PURPOSE_MAP = {
    "samples":        FilePurpose.ORDER_SAMPLE,
    "outlines":       FilePurpose.ORDER_OUTLINE,
    "questionnaires": FilePurpose.ORDER_QUESTIONNAIRE,
    "notes":          FilePurpose.ORDER_NOTES,
    "class-materials": FilePurpose.ORDER_CLASS_MATERIAL,
}


class OrderClientMaterialFileUploadView(OrderFileBaseView):
    """
    Generic upload endpoint for typed client materials.
    Resolves purpose from the URL ``material_type`` kwarg.

    POST /orders/<id>/files/<material_type>/
    """

    def post(self, request, order_id: int, material_type: str):
        purpose = _CLIENT_MATERIAL_PURPOSE_MAP.get(material_type)
        if purpose is None:
            raise ValidationError({"material_type": f"Unknown material type: {material_type}"})

        order = self.get_order(request, order_id)
        self.ensure_client_or_staff(order=order, user=request.user)

        serializer = OrderFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.client_upload_material(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
                purpose=purpose,
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderInternalFileUploadView(OrderFileBaseView):
    """
    POST /orders/<id>/files/internal/
    Staff-only internal file upload (not visible to clients or writers).
    """

    def post(self, request, order_id: int):
        order = self.get_order(request, order_id)

        if not self.is_staff(user=request.user):
            raise PermissionDenied("Only staff can upload internal files.")

        serializer = OrderFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            attachment = OrderFileService.staff_upload_internal(
                order=order,
                uploaded_by=request.user,
                uploaded_file=serializer.validated_data["file"],
                notes=serializer.validated_data.get("description", ""),
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(
            OrderFileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class OrderSubmitFinalView(OrderFileBaseView):
    """
    POST /orders/<id>/files/<attachment_id>/submit-final/
    Marks an uploaded ORDER_FINAL attachment as the delivery candidate.
    """

    def post(self, request, order_id: int, attachment_id: int):
        order = self.get_order(request, order_id)

        attachment = get_object_or_404(
            FileAttachmentSelector.for_object(
                website=order.website,
                obj=order,
            ),
            id=attachment_id,
            purpose=FilePurpose.ORDER_FINAL,
        )

        try:
            result = OrderFileService.submit_final(
                order=order,
                attachment=attachment,
                submitted_by=request.user,
            )
        except FileManagementError as exc:
            raise self.handle_file_error(exc) from exc

        return Response(OrderFileAttachmentSerializer(result).data)

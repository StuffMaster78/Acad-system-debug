from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from files_management.api.serializers.serializers import (
    FileAttachSerializer,
    FileAttachmentSerializer,
    FileDeletionRequestSerializer,
    FileUploadSerializer,
)
from files_management.models import FileAttachment, ManagedFile
from files_management.services import (
    FileAttachmentService,
    FileDeletionService,
    FileDownloadService,
    FileUploadService,
)
from files_management.selectors import (
    FileAttachmentSelector,
    ManagedFileSelector,
)
from rest_framework import parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from files_management.models.file_bucket import FileBucket
from files_management.models.file_quota import FileQuota
from files_management.models.managed_file import ManagedFile

from files_management.api.serializers.serializers import (
    FileQuotaSerializer,
    FileUploadSerializer,
    ManagedFileSerializer,
)

class FileUploadView(APIView):
    """
    Upload a file.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = FileUploadService.upload_file(
            website=request.user.website,
            uploaded_by=request.user,
            uploaded_file=serializer.validated_data["file"],
            purpose=serializer.validated_data["purpose"],
            is_public=serializer.validated_data["is_public"],
        )

        return Response(
            {"file_id": file.id},
            status=status.HTTP_201_CREATED,
        )


class FileAttachView(APIView):
    """
    Attach file to domain object.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FileAttachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = ManagedFileSelector.by_id_for_website(
            file_id=serializer.validated_data["file_id"],
            website=request.user.website,
        )

        content_type = ContentType.objects.get(
            model=serializer.validated_data["content_type"]
        )

        obj = content_type.get_object_for_this_type(
            id=serializer.validated_data["object_id"]
        )

        attachment = FileAttachmentService.attach_managed_file(
            website=request.user.website,
            obj=obj,
            managed_file=file,
            purpose=serializer.validated_data["purpose"],
            visibility=serializer.validated_data["visibility"],
            attached_by=request.user,
        )

        return Response(
            FileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class FileDownloadView(APIView):
    """
    Get download URL.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, attachment_id: int):
        attachment = FileAttachmentSelector.by_id_for_website(
            attachment_id=attachment_id,
            website=request.user.website,
        )

        url = FileDownloadService.get_download_url(
            user=request.user,
            website=request.user.website,
            attachment=attachment,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response({"url": url})


class FileDeletionRequestView(APIView):
    """
    Request deletion.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FileDeletionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachment = FileAttachmentSelector.by_id_for_website(
            attachment_id=serializer.validated_data["attachment_id"],
            website=request.user.website,
        )

        req = FileDeletionService.request_deletion(
            website=request.user.website,
            requested_by=request.user,
            attachment=attachment,
            reason=serializer.validated_data["reason"],
            scope=serializer.validated_data["scope"],
        )

        return Response(
            {"request_id": req.id},
            status=status.HTTP_201_CREATED,
        )


class ManagedFileViewSet(viewsets.ReadOnlyModelViewSet):
    """File listing and detail. Upload via the upload action."""

    serializer_class = ManagedFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        site = getattr(self.request, "site", None)
        qs = ManagedFile.objects.filter(parent_file__isnull=True)
        if site:
            qs = qs.filter(site=site)

        file_kind = self.request.query_params.get("kind")
        if file_kind:
            qs = qs.filter(file_kind=file_kind)

        return qs.select_related("bucket").order_by("-created_at")

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[parsers.MultiPartParser],
        serializer_class=FileUploadSerializer,
    )
    def upload(self, request):
        """POST /cms-api/files/upload/ (multipart form)"""
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data["file"]
        bucket_id = serializer.validated_data.get("bucket_id")
        file_kind = serializer.validated_data.get("file_kind", "other")
        is_public = serializer.validated_data.get("is_public", False)

        # Resolve bucket
        if bucket_id:
            try:
                bucket = FileBucket.objects.get(pk=bucket_id)
            except FileBucket.DoesNotExist:
                return Response(
                    {"error": "Bucket not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            bucket_type = "tenant_public" if is_public else "tenant_private"
            site = getattr(request, "site", None)
            bucket = FileBucket.objects.filter(
                bucket_type=bucket_type,
                site=site,
            ).first()
            if not bucket:
                bucket = FileBucket.objects.filter(
                    bucket_type=bucket_type,
                ).first()
            if not bucket:
                return Response(
                    {"error": "No suitable bucket configured"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Get website
        website = getattr(request, "website", None)
        if not website:
            return Response(
                {"error": "No website context"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from files_management.services.storage_service import StorageService

        try:
            managed_file = StorageService.upload(
                file_obj=file_obj,
                bucket=bucket,
                website=website,
                uploaded_by=request.user,
                file_kind=file_kind,
                is_public=is_public,
            )
        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except RuntimeError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            ManagedFileSerializer(managed_file).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def download(self, request, uuid=None):
        """GET /cms-api/files/{uuid}/download/ — get signed download URL."""
        managed_file = self.get_object()
        from files_management.services.storage_service import StorageService

        url = StorageService.get_download_url(managed_file, force_download=True)
        return Response({"download_url": url})

    @action(detail=True, methods=["get"])
    def derivatives(self, request, uuid=None):
        """GET /cms-api/files/{uuid}/derivatives/ — list file derivatives."""
        managed_file = self.get_object()
        derivs = ManagedFile.objects.filter(parent_file=managed_file)
        return Response(ManagedFileSerializer(derivs, many=True).data)

    @action(detail=True, methods=["delete"])
    def soft_delete(self, request, uuid=None):
        """DELETE /cms-api/files/{uuid}/soft_delete/"""
        managed_file = self.get_object()
        from files_management.services.storage_service import StorageService

        StorageService.delete(managed_file, hard=False)
        return Response({"status": "soft_deleted"})


class FileQuotaView(viewsets.ViewSet):
    """GET /cms-api/files/quota/ — current tenant's storage quota."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        website = getattr(request, "website", None)
        if not website:
            return Response({"error": "No website context"}, status=400)

        quota, _ = FileQuota.objects.get_or_create(website=website)
        return Response(FileQuotaSerializer(quota).data)


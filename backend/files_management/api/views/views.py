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
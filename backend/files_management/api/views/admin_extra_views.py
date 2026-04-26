from __future__ import annotations

from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from files_management.api.serializers.admin_serializers import IsTenantStaff
from files_management.api.serializers.admin_extra_serializers import (
    AdminFileReplaceSerializer,
    CMSUploadSerializer,
    ExternalLinkSubmitSerializer,
)
from files_management.api.serializers.serializers import FileAttachmentSerializer
from files_management.models import ExternalFileLink, ManagedFile
from files_management.services import (
    ExternalFileLinkService,
    FileAttachmentService,
    FileUploadService,
    FileVersionService,
)


class AdminFileListView(APIView):
    """
    List and search files across tenant.
    """

    permission_classes = [IsTenantStaff]

    def get(self, request):
        query = request.query_params.get("q", "")

        qs = ManagedFile.objects.filter(
            website=request.user.website,
        )

        if query:
            qs = qs.filter(
                Q(original_name__icontains=query)
                | Q(mime_type__icontains=query)
                | Q(storage_key__icontains=query)
            )

        qs = qs.order_by("-created_at")[:100]

        data = [
            {
                "id": f.id,
                "name": f.original_name,
                "size": f.file_size,
                "type": f.mime_type,
                "status": f.lifecycle_status,
                "created_at": f.created_at,
            }
            for f in qs
        ]

        return Response(data)


class AdminFileReplaceView(APIView):
    """
    Replace file (versioning).
    """

    permission_classes = [IsTenantStaff]

    def post(self, request, attachment_id: int):
        serializer = AdminFileReplaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from files_management.selectors import FileAttachmentSelector

        attachment = FileAttachmentSelector.by_id_for_website(
            attachment_id=attachment_id,
            website=request.user.website,
        )

        updated_attachment = FileVersionService.replace_attachment_file(
            website=request.user.website,
            replaced_by=request.user,
            attachment=attachment,
            uploaded_file=serializer.validated_data["file"],
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            FileAttachmentSerializer(updated_attachment).data
        )


class AdminExternalLinkListCreateView(APIView):
    """
    Submit and list external links.
    """

    permission_classes = [IsTenantStaff]

    def get(self, request):
        links = ExternalFileLink.objects.filter(
            website=request.user.website,
        ).order_by("-created_at")[:100]

        data = [
            {
                "id": l.id,
                "url": l.url,
                "status": l.review_status,
                "provider": l.provider,
                "created_at": l.created_at,
            }
            for l in links
        ]

        return Response(data)

    def post(self, request):
        serializer = ExternalLinkSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        link = ExternalFileLinkService.submit_link(
            website=request.user.website,
            submitted_by=request.user,
            url=serializer.validated_data["url"],
            purpose=serializer.validated_data["purpose"],
            title=serializer.validated_data.get("title", ""),
        )

        return Response(
            {"id": link.id, "status": link.review_status},
            status=status.HTTP_201_CREATED,
        )


class CMSFileUploadView(APIView):
    """
    Content manager upload endpoint.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request):
        serializer = CMSUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = FileUploadService.upload_file(
            website=request.user.website,
            uploaded_by=request.user,
            uploaded_file=serializer.validated_data["file"],
            purpose=serializer.validated_data["purpose"],
            is_public=True,
        )

        # CMS usually attaches later to page/content
        return Response(
            {
                "file_id": file.id,
                "name": file.original_name,
            },
            status=status.HTTP_201_CREATED,
        )
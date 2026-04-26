from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from files_management.api.serializers.admin_serializers import (
    AdminDeletionCompleteSerializer,
    AdminDeletionRejectSerializer,
    AdminDeletionReviewSerializer,
    AdminExternalLinkReviewSerializer,
    AdminQuarantineReleaseSerializer,
    FileAccessGrantCreateSerializer,
    FileAccessGrantSerializer,
    FileDeletionRequestAdminSerializer,
    FilePolicySerializer,
)
from files_management.models import (
    ExternalFileLink,
    FileAccessGrant,
    FileAttachment,
    FileDeletionRequest,
    FilePolicy,
    ManagedFile,
)
from files_management.services import (
    ExternalFileLinkService,
    FileAccessGrantService,
    FileDeletionService,
    FileScanService,
)


class IsTenantStaff(IsAuthenticated):
    """
    Permission allowing only authenticated tenant staff.

    This is intentionally defensive because role names may still be
    evolving across the refactor.
    """

    def has_permission(self, request, view) -> bool:
        """
        Return whether the user can manage files for a tenant.
        """

        if not super().has_permission(request, view):
            return False

        user = request.user

        return bool(
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
            or getattr(user, "is_super_admin", False)
            or getattr(user, "is_content_manager", False)
        )


class AdminExternalFileLinkApproveView(APIView):
    """
    Approve an external file link after staff review.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request, link_id: int):
        serializer = AdminExternalLinkReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        external_link = ExternalFileLink.objects.get(
            id=link_id,
            website=request.user.website,
        )

        external_link = ExternalFileLinkService.approve_link(
            external_link=external_link,
            reviewed_by=request.user,
            review_note=serializer.validated_data.get("review_note", ""),
        )

        return Response(
            {"id": external_link.id, "status": external_link.review_status}
        )


class AdminExternalFileLinkRejectView(APIView):
    """
    Reject an external file link after staff review.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request, link_id: int):
        serializer = AdminExternalLinkReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        external_link = ExternalFileLink.objects.get(
            id=link_id,
            website=request.user.website,
        )

        external_link = ExternalFileLinkService.reject_link(
            external_link=external_link,
            reviewed_by=request.user,
            review_note=serializer.validated_data.get("review_note", ""),
        )

        return Response(
            {"id": external_link.id, "status": external_link.review_status}
        )


class AdminDeletionRequestListView(ListCreateAPIView):
    """
    List deletion requests for staff review.

    Creation remains available mostly for staff initiated requests, but
    normal client/writer deletion requests should use the public request
    endpoint.
    """

    permission_classes = [IsTenantStaff]
    serializer_class = FileDeletionRequestAdminSerializer

    def get_queryset(self):
        """
        Return deletion requests for the current tenant.
        """

        return FileDeletionRequest.objects.filter(
            website=self.request.user.website,
        ).order_by("-created_at")


class AdminDeletionRequestApproveView(APIView):
    """
    Approve a pending deletion request.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request, request_id: int):
        serializer = AdminDeletionReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deletion_request = FileDeletionRequest.objects.get(
            id=request_id,
            website=request.user.website,
        )

        deletion_request = FileDeletionService.approve_request(
            deletion_request=deletion_request,
            reviewed_by=request.user,
            admin_comment=serializer.validated_data.get(
                "admin_comment",
                "",
            ),
        )

        return Response(
            {"id": deletion_request.id, "status": deletion_request.status}
        )


class AdminDeletionRequestRejectView(APIView):
    """
    Reject a pending deletion request.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request, request_id: int):
        serializer = AdminDeletionRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deletion_request = FileDeletionRequest.objects.get(
            id=request_id,
            website=request.user.website,
        )

        deletion_request = FileDeletionService.reject_request(
            deletion_request=deletion_request,
            reviewed_by=request.user,
            admin_comment=serializer.validated_data["admin_comment"],
        )

        return Response(
            {"id": deletion_request.id, "status": deletion_request.status}
        )


class AdminDeletionRequestCompleteView(APIView):
    """
    Complete an approved deletion request.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request, request_id: int):
        serializer = AdminDeletionCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deletion_request = FileDeletionRequest.objects.get(
            id=request_id,
            website=request.user.website,
        )

        deletion_request = FileDeletionService.complete_request(
            deletion_request=deletion_request,
            completed_by=request.user,
            admin_comment=serializer.validated_data.get(
                "admin_comment",
                "",
            ),
        )

        return Response(
            {"id": deletion_request.id, "status": deletion_request.status}
        )


class AdminFilePolicyListCreateView(ListCreateAPIView):
    """
    List and create tenant file policies.
    """

    permission_classes = [IsTenantStaff]
    serializer_class = FilePolicySerializer

    def get_queryset(self):
        """
        Return policies for the current tenant.
        """

        return FilePolicy.objects.filter(
            website=self.request.user.website,
        ).order_by("purpose")

    def perform_create(self, serializer) -> None:
        """
        Create a policy for the current tenant.
        """

        serializer.save(website=self.request.user.website)


class AdminFilePolicyDetailView(RetrieveUpdateAPIView):
    """
    Retrieve or update a tenant file policy.
    """

    permission_classes = [IsTenantStaff]
    serializer_class = FilePolicySerializer
    lookup_url_kwarg = "policy_id"

    def get_queryset(self):
        """
        Return policies for the current tenant.
        """

        return FilePolicy.objects.filter(
            website=self.request.user.website,
        )


class AdminFileAccessGrantCreateView(APIView):
    """
    Grant explicit temporary or permanent file access.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request):
        serializer = FileAccessGrantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user_model = get_user_model()

        managed_file = ManagedFile.objects.get(
            id=data["managed_file_id"],
            website=request.user.website,
        )
        grantee = user_model.objects.get(
            id=data["grantee_id"],
            website=request.user.website,
        )

        attachment = None

        if data.get("attachment_id"):
            attachment = FileAttachment.objects.get(
                id=data["attachment_id"],
                website=request.user.website,
            )

        grant = FileAccessGrantService.grant_access(
            website=request.user.website,
            managed_file=managed_file,
            grantee=grantee,
            granted_by=request.user,
            action=data["action"],
            attachment=attachment,
            reason=data.get("reason", ""),
            expires_at=data.get("expires_at"),
        )

        return Response(
            FileAccessGrantSerializer(grant).data,
            status=status.HTTP_201_CREATED,
        )


class AdminFileAccessGrantRevokeView(APIView):
    """
    Revoke an explicit file access grant.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request, grant_id: int):
        grant = FileAccessGrant.objects.get(
            id=grant_id,
            website=request.user.website,
        )

        grant = FileAccessGrantService.revoke_access(
            access_grant=grant,
            revoked_by=request.user,
        )

        return Response(FileAccessGrantSerializer(grant).data)


class AdminQuarantineReleaseView(APIView):
    """
    Release a quarantined file after staff review.
    """

    permission_classes = [IsTenantStaff]

    def post(self, request, file_id: int):
        serializer = AdminQuarantineReleaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        managed_file = ManagedFile.objects.get(
            id=file_id,
            website=request.user.website,
        )

        managed_file = FileScanService.release_from_quarantine(
            managed_file=managed_file,
            released_by=request.user,
            summary=serializer.validated_data.get("summary", ""),
        )

        return Response(
            {
                "id": managed_file.id,
                "lifecycle_status": managed_file.lifecycle_status,
                "scan_status": managed_file.scan_status,
            }
        )
"""
Views for WriterProfile.
"""
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from writer_management.api.permissions import (
    IsAdminUser, IsWriterUser, IsAdminOrWriterOwner,
)
from writer_management.api.filters.writer_filters import WriterProfileFilter
from writer_management.api.serializers.profile_serializers import (
    WriterProfileSummarySerializer,
    WriterProfileDetailSerializer,
    WriterProfilePublicSerializer,
    WriterProfileUpdateSerializer,
)
from writer_management.models.writer_profile import WriterProfile
from writer_management.services.writer_profile_service import WriterProfileService
from writer_management.utils import (
    get_writer_profile_for_website,
    require_writer_profile,
)
from writer_management.api.permissions import _resolve_website


class WriterProfileListView(ListAPIView):
    """
    GET /api/writer-management/writers/
    Admin: list all writers on the website with filters.
    """
    permission_classes = [IsAdminUser]
    serializer_class = WriterProfileSummarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WriterProfileFilter

    def get_queryset(self):
        website = _resolve_website(self.request)
        return (
            WriterProfile.objects.filter(
                writer_level__website=website,
            )
            .select_related(
                "writer_level",
                "account_profile__user",
                "capacity",
                "discipline_state",
            )
            .order_by("-joined_at")
        )


class WriterProfileDetailView(RetrieveAPIView):
    """
    GET /api/writer-management/writers/<registration_id>/
    Admin: full writer profile detail.
    """
    permission_classes = [IsAdminUser]
    serializer_class = WriterProfileDetailSerializer
    lookup_field = "registration_id"

    def get_queryset(self):
        website = _resolve_website(self.request)
        return WriterProfile.objects.filter(
            writer_level__website=website,
        ).select_related(
            "writer_level",
            "writer_level__settings",
            "account_profile__user",
            "capacity",
            "discipline_state",
        )


class MyWriterProfileView(APIView):
    """
    GET  /api/writer-management/me/profile/
    PATCH /api/writer-management/me/profile/

    Writer: view and update their own profile.
    """
    permission_classes = [IsWriterUser]

    def get(self, request):
        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
        if profile is None:
            return Response(
                {"detail": "Writer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = WriterProfileDetailSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
        if profile is None:
            return Response(
                {"detail": "Writer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = WriterProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = WriterProfileService.update_profile(
            writer=profile,
            updated_by=request.user,
            is_admin=False,
            **serializer.validated_data,
        )
        return Response(WriterProfileDetailSerializer(updated).data)


class WriterPublicCardView(RetrieveAPIView):
    """
    GET /api/writer-management/writers/<public_uuid>/card/
    Public client-facing writer card.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WriterProfilePublicSerializer
    lookup_field = "public_uuid"

    def get_queryset(self):
        return WriterProfile.objects.filter(
            is_deleted=False,
        ).select_related("writer_level")


class SoftDeleteWriterView(APIView):
    """
    POST /api/writer-management/writers/<registration_id>/delete/
    Admin: soft delete a writer profile.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        try:
            profile = WriterProfileService.get_by_registration_id(
                registration_id
            )
        except Exception:
            return Response(
                {"detail": "Writer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        reason = request.data.get("reason", "")
        WriterProfileService.soft_delete(
            writer=profile,
            deleted_by=request.user,
            reason=reason,
        )
        return Response({"detail": "Writer profile deleted."})


class RestoreWriterView(APIView):
    """
    POST /api/writer-management/writers/<registration_id>/restore/
    Admin: restore a soft-deleted writer.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        try:
            profile = WriterProfileService.get_by_registration_id(
                registration_id
            )
        except Exception:
            return Response(
                {"detail": "Writer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        reason = request.data.get("reason", "")
        try:
            WriterProfileService.restore(
                writer=profile,
                restored_by=request.user,
                reason=reason,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Writer profile restored."})
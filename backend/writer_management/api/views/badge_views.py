"""
Admin endpoints for manually awarding and revoking writer badges,
and for awarding/adjusting loyalty points for writers.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_management.api.permissions import IsAdminOrWriterOwner


def _require_staff(request) -> bool:
    role = getattr(request.user, "role", None)
    return role in ("admin", "superadmin", "support") or request.user.is_superuser


class AdminBadgeListView(APIView):
    """
    GET  /api/writer-management/badges/        — list all badge definitions
    POST /api/writer-management/badges/        — create a badge definition
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        from writer_management.models.old_models.badges import Badge
        from writer_management.api.serializers.badge_serializers import BadgeSerializer
        website = getattr(request, "website", None)
        qs = Badge.objects.filter(is_active=True)
        if website:
            qs = qs.filter(website=website)
        return Response(BadgeSerializer(qs, many=True).data)

    def post(self, request):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        from writer_management.api.serializers.badge_serializers import BadgeSerializer
        serializer = BadgeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdminWriterBadgeAwardView(APIView):
    """
    POST /api/writer-management/writers/<registration_id>/badges/award/
    Award a badge to a writer manually.

    Body: { "badge_id": int, "notes": str (optional) }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, registration_id: str):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)

        from writer_management.models.old_models.badges import Badge, WriterBadge
        from writer_management.services.writer_profile_service import WriterProfileService

        badge_id = request.data.get("badge_id")
        notes = request.data.get("notes", "")

        if not badge_id:
            return Response({"detail": "badge_id is required."}, status=400)

        try:
            writer = WriterProfileService.get_by_registration_id(registration_id)
        except Exception:
            return Response({"detail": "Writer not found."}, status=404)

        try:
            badge = Badge.objects.get(pk=badge_id, is_active=True)
        except Badge.DoesNotExist:
            return Response({"detail": "Badge not found."}, status=404)

        writer_badge, created = WriterBadge.objects.get_or_create(
            writer=writer,
            badge=badge,
            revoked=False,
            defaults={
                "is_auto_awarded": False,
                "notes": notes,
            },
        )

        if not created:
            return Response({"detail": "Writer already holds this badge."}, status=400)

        return Response(
            {
                "id": writer_badge.pk,
                "badge_id": badge.pk,
                "badge_name": badge.name,
                "writer_id": getattr(writer, "pk", None),
                "issued_at": writer_badge.issued_at,
                "notes": writer_badge.notes,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminWriterBadgeRevokeView(APIView):
    """
    POST /api/writer-management/writer-badges/<pk>/revoke/
    Revoke a badge from a writer.

    Body: { "reason": str }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)

        from django.utils import timezone
        from writer_management.models.old_models.badges import WriterBadge

        try:
            writer_badge = WriterBadge.objects.get(pk=pk, revoked=False)
        except WriterBadge.DoesNotExist:
            return Response({"detail": "Active badge record not found."}, status=404)

        writer_badge.revoked = True
        writer_badge.revoked_at = timezone.now()
        writer_badge.revoked_reason = request.data.get("reason", "")
        writer_badge.revoked_by = request.user
        writer_badge.save(update_fields=["revoked", "revoked_at", "revoked_reason", "revoked_by"])

        return Response({"detail": "Badge revoked."})


class AdminWriterBadgeListView(APIView):
    """
    GET /api/writer-management/writers/<registration_id>/badges/
    List all active badges for a writer.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, registration_id: str):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)

        from writer_management.models.old_models.badges import WriterBadge
        from writer_management.services.writer_profile_service import WriterProfileService

        try:
            writer = WriterProfileService.get_by_registration_id(registration_id)
        except Exception:
            return Response({"detail": "Writer not found."}, status=404)

        badges = WriterBadge.objects.filter(writer=writer, revoked=False).select_related("badge")
        data = [
            {
                "id": wb.pk,
                "badge_id": wb.badge.pk,
                "badge_name": wb.badge.name,
                "badge_icon": wb.badge.icon,
                "badge_type": wb.badge.type,
                "is_auto_awarded": wb.is_auto_awarded,
                "issued_at": wb.issued_at,
                "notes": wb.notes,
            }
            for wb in badges
        ]
        return Response(data)

"""
Admin API for viewing and updating WriterLevel + WriterLevelSettings.
"""
from __future__ import annotations

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def _require_staff(request) -> bool:
    role = getattr(request.user, "role", None)
    return role in ("admin", "superadmin") or request.user.is_superuser


class WriterLevelSettingsSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source="writer_level.name", read_only=True)
    level_id = serializers.IntegerField(source="writer_level.id", read_only=True)

    class Meta:
        from writer_management.models.writer_level_settings import WriterLevelSettings
        model = WriterLevelSettings
        fields = [
            "id", "level_id", "level_name",
            "max_active_orders", "max_manual_takes", "max_pending_assignments",
            "base_pay_per_page",
        ]
        read_only_fields = ["id", "level_id", "level_name"]


class WriterLevelSettingsListView(APIView):
    """
    GET  /api/v1/writer-management/level-settings/  — list all level settings
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        from writer_management.models.writer_level_settings import WriterLevelSettings
        qs = WriterLevelSettings.objects.select_related("writer_level").all()
        return Response(WriterLevelSettingsSerializer(qs, many=True).data)


class WriterLevelSettingsDetailView(APIView):
    """
    GET   /api/v1/writer-management/level-settings/<pk>/
    PATCH /api/v1/writer-management/level-settings/<pk>/
    """
    permission_classes = [IsAuthenticated]

    def _get(self, pk):
        from writer_management.models.writer_level_settings import WriterLevelSettings
        try:
            return WriterLevelSettings.objects.select_related("writer_level").get(pk=pk)
        except WriterLevelSettings.DoesNotExist:
            return None

    def get(self, request, pk: int):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        obj = self._get(pk)
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        return Response(WriterLevelSettingsSerializer(obj).data)

    def patch(self, request, pk: int):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        obj = self._get(pk)
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        serializer = WriterLevelSettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

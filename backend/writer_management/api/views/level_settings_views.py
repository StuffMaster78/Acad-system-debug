"""
Admin API for WriterLevel CRUD and full WriterLevelSettings management.
"""
from __future__ import annotations

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def _require_staff(request) -> bool:
    role = getattr(request.user, "role", None)
    return role in ("admin", "superadmin") or request.user.is_superuser


def _resolve_website(request):
    w = getattr(request, "website", None)
    if w:
        return w
    try:
        return request.user.account_profiles.order_by("pk").first().website
    except Exception:
        return None


def _is_superadmin(request) -> bool:
    return getattr(request.user, "role", None) == "superadmin" or request.user.is_superuser


def _resolve_requested_website(request):
    """
    Resolve the website scope for writer level configuration.

    Superadmin may pass ?website_id=... for cross-site management. Admins are
    always constrained to their resolved request/user website.
    """
    website = _resolve_website(request)
    if _is_superadmin(request):
        website_id = request.query_params.get("website_id") or request.data.get("website_id")
        if website_id:
            from websites.models.websites import Website
            try:
                return Website.objects.get(pk=website_id)
            except Website.DoesNotExist:
                return None
    return website


# ── Serializers ───────────────────────────────────────────────────────────────

class WriterLevelSerializer(serializers.ModelSerializer):
    """Full writer level — name, order, default flag."""
    settings_id = serializers.SerializerMethodField()

    class Meta:
        from writer_management.models.writer_level import WriterLevel
        model = WriterLevel
        fields = [
            "id", "name", "description", "display_order",
            "is_active", "is_default", "settings_id",
        ]
        read_only_fields = ["id", "settings_id"]

    def get_settings_id(self, obj):
        try:
            return obj.settings.id
        except Exception:
            return None


class WriterLevelSettingsSerializer(serializers.ModelSerializer):
    level_id   = serializers.IntegerField(source="writer_level.id",   read_only=True)
    level_name = serializers.CharField(source="writer_level.name",    read_only=True)

    class Meta:
        from writer_management.models.writer_level_settings import WriterLevelSettings
        model = WriterLevelSettings
        fields = [
            "id", "level_id", "level_name",
            # Pay rates
            "base_pay_per_page", "base_pay_per_slide", "base_pay_per_chart",
            "additional_page_pay", "additional_slide_pay", "additional_chart_pay",
            # Tip retention
            "tip_percentage",
            # Capacity
            "max_active_orders", "max_manual_takes", "max_pending_assignments",
            # Urgency
            "urgent_time_threshold_hours", "urgent_order_surcharge", "urgent_multiplier",
            # Promotion eligibility
            "min_completed_orders", "min_rating", "min_successful_takes",
            "min_completion_rate", "max_revision_rate", "max_lateness_rate",
            "max_warnings",
            # Status
            "is_active",
        ]
        read_only_fields = ["id", "level_id", "level_name"]


# ── Writer Level CRUD ─────────────────────────────────────────────────────────

class WriterLevelListCreateView(APIView):
    """
    GET  /writer-management/levels/       list all levels for this website
    POST /writer-management/levels/       create a new level
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        from writer_management.models.writer_level import WriterLevel
        website = _resolve_requested_website(request)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)
        qs = WriterLevel.objects.filter(website=website).order_by("display_order", "name")
        return Response(WriterLevelSerializer(qs, many=True).data)

    def post(self, request):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        from writer_management.models.writer_level import WriterLevel
        from writer_management.models.writer_level_settings import WriterLevelSettings
        website = _resolve_requested_website(request)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)
        s = WriterLevelSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        level = WriterLevel.objects.create(website=website, **s.validated_data)
        # Bootstrap empty settings row
        WriterLevelSettings.objects.get_or_create(writer_level=level)
        return Response(WriterLevelSerializer(level).data, status=status.HTTP_201_CREATED)


class WriterLevelDetailView(APIView):
    """
    GET    /writer-management/levels/<pk>/
    PATCH  /writer-management/levels/<pk>/
    DELETE /writer-management/levels/<pk>/
    """
    permission_classes = [IsAuthenticated]

    def _get(self, pk, website):
        from writer_management.models.writer_level import WriterLevel
        try:
            return WriterLevel.objects.get(pk=pk, website=website)
        except WriterLevel.DoesNotExist:
            return None

    def get(self, request, pk: int):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        website = _resolve_requested_website(request)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)
        obj = self._get(pk, website)
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        return Response(WriterLevelSerializer(obj).data)

    def patch(self, request, pk: int):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        website = _resolve_requested_website(request)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)
        obj = self._get(pk, website)
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        s = WriterLevelSerializer(obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        # Only one default per website
        if s.validated_data.get("is_default"):
            from writer_management.models.writer_level import WriterLevel
            WriterLevel.objects.filter(website=obj.website, is_default=True).exclude(
                pk=pk
            ).update(is_default=False)
        s.save()
        return Response(WriterLevelSerializer(obj).data)

    def delete(self, request, pk: int):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        website = _resolve_requested_website(request)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)
        obj = self._get(pk, website)
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        if obj.is_default:
            return Response(
                {"detail": "Cannot delete the default writer level."},
                status=400,
            )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Writer Level Settings ─────────────────────────────────────────────────────

class WriterLevelSettingsListView(APIView):
    """GET  /writer-management/level-settings/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        from writer_management.models.writer_level_settings import WriterLevelSettings
        website = _resolve_requested_website(request)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)
        qs = WriterLevelSettings.objects.select_related("writer_level").filter(
            writer_level__website=website,
        )
        return Response(WriterLevelSettingsSerializer(qs, many=True).data)


class WriterLevelSettingsDetailView(APIView):
    """
    GET   /writer-management/level-settings/<pk>/
    PATCH /writer-management/level-settings/<pk>/
    """
    permission_classes = [IsAuthenticated]

    def _get(self, pk, website):
        from writer_management.models.writer_level_settings import WriterLevelSettings
        try:
            return WriterLevelSettings.objects.select_related("writer_level").get(
                pk=pk,
                writer_level__website=website,
            )
        except WriterLevelSettings.DoesNotExist:
            return None

    def get(self, request, pk: int):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        website = _resolve_requested_website(request)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)
        obj = self._get(pk, website)
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        return Response(WriterLevelSettingsSerializer(obj).data)

    def patch(self, request, pk: int):
        if not _require_staff(request):
            return Response({"detail": "Forbidden."}, status=403)
        website = _resolve_requested_website(request)
        if website is None:
            return Response({"detail": "Website context required."}, status=400)
        obj = self._get(pk, website)
        if obj is None:
            return Response({"detail": "Not found."}, status=404)
        s = WriterLevelSettingsSerializer(obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(WriterLevelSettingsSerializer(obj).data)

from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import QAChecklistItem, QAChecklistResult, QAChecklistTemplate

STAFF_ROLES = {"admin", "superadmin", "editor", "support"}


def _is_staff(user) -> bool:
    return bool(getattr(user, "is_staff", False)) or getattr(user, "role", "") in STAFF_ROLES


# ── Serializers ──────────────────────────────────────────────────────────────

class QAItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAChecklistItem
        fields = ["id", "category", "text", "is_required", "display_order"]


class QATemplateSerializer(serializers.ModelSerializer):
    items = QAItemSerializer(many=True, read_only=True)

    class Meta:
        model = QAChecklistTemplate
        fields = ["id", "name", "description", "is_default", "items"]


class QAResultSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    reviewer_name = serializers.SerializerMethodField()
    pass_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = QAChecklistResult
        fields = [
            "id", "order", "template", "template_name",
            "reviewer", "reviewer_name",
            "checked_items", "verdict", "notes", "pass_rate",
            "completed_at", "created_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at", "completed_at"]

    def get_reviewer_name(self, obj) -> str:
        return obj.reviewer.get_full_name() or obj.reviewer.username


# ── Views ─────────────────────────────────────────────────────────────────────

class QATemplateListView(APIView):
    """GET /api/v1/qa/templates/  — list active templates for the caller's website."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        website = getattr(request, "website", None)
        qs = QAChecklistTemplate.objects.filter(is_active=True).prefetch_related("items")
        if website:
            qs = qs.filter(website__in=[website, None])
        return Response(QATemplateSerializer(qs, many=True).data)


class QAResultView(APIView):
    """
    GET  /api/v1/qa/orders/{order_id}/results/  — list QA results for an order
    POST /api/v1/qa/orders/{order_id}/results/  — submit or update a QA result
    """

    permission_classes = [IsAuthenticated]

    def _get_order(self, order_id: int):
        from orders.models.orders import Order
        try:
            return Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return None

    def get(self, request, order_id: int):
        order = self._get_order(order_id)
        if order is None:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        results = QAChecklistResult.objects.filter(order=order).select_related(
            "template", "reviewer"
        )
        return Response(QAResultSerializer(results, many=True).data)

    def post(self, request, order_id: int):
        if not _is_staff(request.user):
            return Response(
                {"detail": "Only staff may submit QA results."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = self._get_order(order_id)
        if order is None:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        template_id = request.data.get("template_id")
        if not template_id:
            return Response({"detail": "template_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            template = QAChecklistTemplate.objects.get(pk=template_id)
        except QAChecklistTemplate.DoesNotExist:
            return Response({"detail": "Template not found."}, status=status.HTTP_404_NOT_FOUND)

        checked_items = request.data.get("checked_items", [])
        verdict = request.data.get("verdict")
        notes = request.data.get("notes", "")

        result, _ = QAChecklistResult.objects.get_or_create(
            order=order,
            reviewer=request.user,
            template=template,
            defaults={"checked_items": checked_items, "verdict": verdict, "notes": notes},
        )

        if not _:
            result.checked_items = checked_items
            result.verdict = verdict
            result.notes = notes
            if verdict:
                result.completed_at = timezone.now()
            result.save()

        return Response(
            QAResultSerializer(result).data,
            status=status.HTTP_201_CREATED if _ else status.HTTP_200_OK,
        )

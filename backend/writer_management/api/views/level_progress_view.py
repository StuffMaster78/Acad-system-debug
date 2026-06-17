from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class WriterLevelProgressView(APIView):
    """
    GET /api/writer-management/me/level/

    Returns the writer's current level, their performance against
    that level's criteria, and the next level's requirements.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from writer_management.models.writer_profile import WriterProfile
        from writer_management.models.writer_performance import WriterPerformance
        from writer_management.models.writer_level import WriterLevel

        try:
            profile = WriterProfile.objects.select_related(
                "writer_level",
            ).get(account_profile__user=request.user)
        except WriterProfile.DoesNotExist:
            return Response({"detail": "Writer profile not found."}, status=404)

        current_level = profile.writer_level
        performance = self._get_performance(profile)

        payload = {
            "current": self._level_data(current_level),
            "criteria": self._criteria_data(current_level),
            "performance": performance,
            "next": self._next_level(current_level),
        }
        return Response(payload)

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _level_data(level) -> dict | None:
        if level is None:
            return None
        return {
            "id": level.pk,
            "name": level.name,
            "description": level.description or "",
            "display_order": level.display_order,
        }

    @staticmethod
    def _criteria_data(level) -> dict:
        if level is None:
            return {}
        try:
            c = level.criteria
        except Exception:
            return {}
        return {
            "min_orders_completed": c.min_orders_completed,
            "min_completion_rate": str(c.min_completion_rate),
            "min_composite_score": str(c.min_composite_score),
            "max_revision_rate": str(c.max_revision_rate) if c.max_revision_rate is not None else None,
            "max_lateness_rate": str(c.max_lateness_rate) if c.max_lateness_rate is not None else None,
        }

    @staticmethod
    def _get_performance(profile) -> dict:
        try:
            from writer_management.models.writer_performance import WriterPerformance
            perf = WriterPerformance.objects.get(writer=profile)
        except Exception:
            return {
                "completed_orders": 0,
                "average_rating": None,
                "completion_rate": None,
                "on_time_rate": None,
                "revision_rate": None,
            }

        def pct(numerator, denominator) -> str | None:
            if not denominator:
                return None
            return str(
                (Decimal(str(numerator)) / Decimal(str(denominator)) * 100)
                .quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            )

        return {
            "completed_orders": perf.completed_orders,
            "average_rating": str(perf.average_rating) if perf.average_rating is not None else None,
            "completion_rate": pct(perf.completed_orders, perf.total_orders) if hasattr(perf, "total_orders") else None,
            "on_time_rate": pct(perf.on_time_deliveries, perf.completed_orders),
            "revision_rate": pct(perf.revision_count, perf.completed_orders),
        }

    @staticmethod
    def _next_level(current_level) -> dict | None:
        if current_level is None:
            return None
        try:
            from writer_management.models.writer_level import WriterLevel
            next_level = (
                WriterLevel.objects
                .filter(
                    website=current_level.website,
                    display_order__gt=current_level.display_order,
                )
                .order_by("display_order")
                .select_related("criteria")
                .first()
            )
            if next_level is None:
                return None
            try:
                c = next_level.criteria
                criteria = {
                    "min_orders_completed": c.min_orders_completed,
                    "min_completion_rate": str(c.min_completion_rate),
                    "min_composite_score": str(c.min_composite_score),
                    "max_revision_rate": str(c.max_revision_rate) if c.max_revision_rate is not None else None,
                    "max_lateness_rate": str(c.max_lateness_rate) if c.max_lateness_rate is not None else None,
                }
            except Exception:
                criteria = {}
            return {
                "id": next_level.pk,
                "name": next_level.name,
                "description": next_level.description or "",
                "criteria": criteria,
            }
        except Exception:
            return None

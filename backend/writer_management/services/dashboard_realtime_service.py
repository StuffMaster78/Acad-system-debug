from __future__ import annotations

import json
from decimal import Decimal

from django.utils import timezone
from django.db.models import Q

from orders.models import Order, WriterRequest
from writer_management.models.requests import WriterOrderRequest
from writer_management.models.configs import WriterLevelConfig
from writer_management.models.metrics import WriterPerformanceMetrics


class WriterDashboardRealtimeService:
    """
    Helper that aggregates frequently changing dashboard metrics for writers.
    Used by the SSE stream to keep widgets updated without heavy polling.
    """

    ACTIVE_ASSIGNMENT_STATUSES = [
        "assigned",
        "in_progress",
        "revision_requested",
        "under_editing",
        "on_revision",
        "on_hold",
        "ready_for_review",
        "ready_for_completion",
    ]

    READY_FOR_SUBMISSION_STATUSES = [
        "ready_for_review",
        "ready_for_completion",
        "in_progress",
        "revision_requested",
        "under_editing",
    ]

    EXCLUDED_DEADLINE_STATUSES = [
        "completed",
        "approved",
        "cancelled",
        "refunded",
        "closed",
        "archived",
    ]

    @classmethod
    def build_payload(cls, user):
        profile = getattr(user, "writer_profile", None)
        if not profile:
            return {"error": "writer_profile_missing"}

        return {
            "timestamp": timezone.now().isoformat(),
            "availability": cls._availability_payload(profile),
            "queue": cls._queue_payload(profile, user),
            "orders_ready": cls._orders_ready_payload(user),
            "next_deadline": cls._next_deadline_payload(user),
            "goal_progress": cls._goal_progress_payload(profile),
            "active_assignments": {
                "count": cls._active_assignment_count(user),
            },
        }

    # ------------------------------------------------------------------ helpers
    @classmethod
    def _availability_payload(cls, profile):
        return {
            "is_available": bool(getattr(profile, "is_available_for_auto_assignments", True)),
            "last_changed": profile.availability_last_changed.isoformat()
            if getattr(profile, "availability_last_changed", None)
            else None,
            "message": profile.availability_message or "",
            "last_active": profile.last_active.isoformat() if profile.last_active else None,
        }

    @classmethod
    def _queue_payload(cls, profile, user):
        base_available = Order.objects.filter(
            status="available",
            website=profile.website,
            assigned_writer__isnull=True,
            is_paid=True,
        )

        preferred_qs = base_available.filter(preferred_writer=user)
        preferred_count = preferred_qs.count()

        common_qs = base_available.filter(preferred_writer__isnull=True)
        common_count = common_qs.count()

        writer_request_count = WriterOrderRequest.objects.filter(
            writer=profile,
            approved=False,
        ).count()

        adjustment_requests = WriterRequest.objects.filter(
            requested_by_writer=user,
            status__in=["pending"],
        ).count()

        return {
            "available": common_count + preferred_count,
            "preferred": preferred_count,
            "requests": writer_request_count + adjustment_requests,
        }

    @classmethod
    def _orders_ready_payload(cls, user):
        qs = (
            Order.objects.filter(
                assigned_writer=user,
                status__in=cls.READY_FOR_SUBMISSION_STATUSES,
            )
            .select_related("client")
            .order_by("writer_deadline", "client_deadline")
        )
        total = qs.count()
        orders = [
            {
                "id": order.id,
                "topic": order.topic or "Untitled order",
                "status": order.status,
                "deadline": cls._coalesce_deadline(order),
                "pages": cls._get_order_pages(order),
            }
            for order in qs[:5]
        ]
        return {"count": total, "orders": orders}

    @classmethod
    def _next_deadline_payload(cls, user):
        upcoming = (
            Order.objects.filter(assigned_writer=user)
            .exclude(status__in=cls.EXCLUDED_DEADLINE_STATUSES)
            .order_by("writer_deadline", "client_deadline", "created_at")
        )
        order = upcoming.first()
        if not order:
            return None
        return {
            "order_id": order.id,
            "topic": order.topic or "Untitled order",
            "deadline": cls._coalesce_deadline(order),
            "status": order.status,
        }

    @classmethod
    def _goal_progress_payload(cls, profile):
        try:
            current_level_name = profile.writer_level.name if profile.writer_level else None
            metrics = (
                WriterPerformanceMetrics.objects.filter(writer=profile)
                .order_by("-week_start")
                .first()
            )
            level_configs = list(
                WriterLevelConfig.objects.filter(
                    website=profile.website,
                    is_active=True,
                ).order_by("-priority")
            )
            next_config = None
            if current_level_name:
                for idx, config in enumerate(level_configs):
                    if config.name == current_level_name and idx > 0:
                        next_config = level_configs[idx - 1]
                        break
            elif level_configs:
                next_config = level_configs[0]

            if not next_config or not metrics:
                return None

            current_score = float(metrics.composite_score or Decimal("0"))
            required_score = float(next_config.min_score or Decimal("0"))

            if required_score <= 0:
                return None

            percentage = min(100.0, round((current_score / required_score) * 100, 1))
            return {
                "current_score": current_score,
                "required_score": required_score,
                "progress_percentage": percentage,
                "next_level_name": next_config.name,
                "points_needed": max(0.0, round(required_score - current_score, 2)),
            }
        except Exception:
            return None

    @classmethod
    def _active_assignment_count(cls, user):
        return Order.objects.filter(
            assigned_writer=user,
            status__in=cls.ACTIVE_ASSIGNMENT_STATUSES,
        ).count()

    @staticmethod
    def _get_order_pages(order):
        return (
            getattr(order, "number_of_pages", None)
            or getattr(order, "pages", None)
            or 0
        )

    @staticmethod
    def _coalesce_deadline(order):
        deadline = (
            getattr(order, "writer_deadline", None)
            or getattr(order, "client_deadline", None)
            or getattr(order, "deadline", None)
        )
        return deadline.isoformat() if deadline else None


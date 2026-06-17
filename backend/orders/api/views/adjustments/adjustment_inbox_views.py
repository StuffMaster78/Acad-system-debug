from __future__ import annotations

from typing import Any, cast

from django.db.models import Q, QuerySet
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.api.views.adjustments.adjustment_detail_views import _serialize_adjustment
from orders.models import OrderAdjustmentRequest


class AdjustmentInboxPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class StaffAdjustmentInboxView(APIView):
    """
    Staff-facing adjustment queue for scope changes, extra services,
    counters, funding handoffs, and post-counter escalations.
    """

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AdjustmentInboxPagination

    STAFF_ROLES = {"admin", "superadmin", "editor", "support"}
    ACTIVE_STATUSES = {
        "pending_client_response",
        "client_countered",
        "accepted",
        "funding_pending",
    }

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = cast(Any, request.user)
        if getattr(user, "role", None) not in self.STAFF_ROLES and not getattr(user, "is_staff", False):
            return Response({"detail": "Staff access required."}, status=status.HTTP_403_FORBIDDEN)

        queryset = self._base_queryset(request)
        queryset = self._apply_filters(request, queryset)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        rows = [self._serialize_row(item) for item in page or queryset]
        if page is not None:
            return paginator.get_paginated_response(rows)
        return Response(rows)

    def _base_queryset(self, request: Request) -> QuerySet[OrderAdjustmentRequest]:
        user = cast(Any, request.user)
        queryset = OrderAdjustmentRequest.objects.select_related(
            "website",
            "order",
            "order__client",
            "requested_by",
            "countered_by",
            "reviewed_by",
            "resolved_by",
        ).prefetch_related("proposals")

        website_id = request.query_params.get("website_id")
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        elif getattr(user, "role", None) != "superadmin":
            website = getattr(request, "website", None) or getattr(user, "website", None)
            queryset = queryset.filter(website=website)

        return queryset.order_by("-escalated_after_counter", "-updated_at", "-created_at")

    def _apply_filters(
        self,
        request: Request,
        queryset: QuerySet[OrderAdjustmentRequest],
    ) -> QuerySet[OrderAdjustmentRequest]:
        status_filter = request.query_params.get("status", "active")
        kind_filter = request.query_params.get("kind", "")
        search = request.query_params.get("q", "").strip()
        escalated = request.query_params.get("escalated", "")

        if status_filter == "active":
            queryset = queryset.filter(status__in=self.ACTIVE_STATUSES)
        elif status_filter and status_filter != "all":
            queryset = queryset.filter(status=status_filter)

        if kind_filter:
            queryset = queryset.filter(adjustment_kind=kind_filter)

        if escalated == "true":
            queryset = queryset.filter(escalated_after_counter=True, resolved_at__isnull=True)
        elif escalated == "false":
            queryset = queryset.filter(Q(escalated_after_counter=False) | Q(resolved_at__isnull=False))

        if search:
            query = (
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(order__topic__icontains=search)
                | Q(order__public_order_number__icontains=search)
            )
            if search.isdigit():
                query |= Q(order_id=int(search)) | Q(id=int(search))
            queryset = queryset.filter(query)

        return queryset

    def _serialize_row(self, adjustment: OrderAdjustmentRequest) -> dict[str, Any]:
        order = adjustment.order
        writer = self._resolve_writer(order)
        data = _serialize_adjustment(adjustment)
        data.update(
            {
                "order_reference": getattr(order, "reference", str(order.pk)),
                "order_topic": getattr(order, "topic", "") or "Untitled order",
                "order_status": getattr(order, "status", ""),
                "website_id": adjustment.website_id,
                "website_name": getattr(adjustment.website, "name", None),
                "client_id": getattr(order, "client_id", None),
                "client_name": self._display_user(getattr(order, "client", None)),
                "writer_id": getattr(writer, "pk", None),
                "writer_name": self._display_user(writer),
                "requires_staff_attention": bool(
                    adjustment.escalated_after_counter and adjustment.resolved_at is None
                ),
            }
        )
        return data

    @staticmethod
    def _display_user(user: Any) -> str:
        if user is None:
            return ""
        full_name = (
            getattr(user, "get_full_name", lambda: "")()
            if callable(getattr(user, "get_full_name", None))
            else ""
        )
        return full_name or getattr(user, "email", "") or getattr(user, "username", "") or str(user.pk)

    @staticmethod
    def _resolve_writer(order: Any) -> Any:
        try:
            return order.assigned_writer
        except Exception:
            return getattr(order, "preferred_writer", None)

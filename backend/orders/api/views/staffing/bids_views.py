"""
/api/v1/bids/ endpoints — writer-facing bid management.

These views expose OrderInterest records in the "Bid" shape the frontend
expects. Backend terminology is "interest"; the UI calls them "bids".
"""
from __future__ import annotations

from typing import Any

from rest_framework import permissions, serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.models.orders.order_interest import OrderInterest
from orders.enums import OrderInterestStatus


class BidSerializer(serializers.ModelSerializer):
    order_id     = serializers.IntegerField(source="order.id", read_only=True)
    order_topic  = serializers.SerializerMethodField()
    writer_id    = serializers.IntegerField(source="writer.id", read_only=True)
    writer_username = serializers.SerializerMethodField()
    writer_rating   = serializers.SerializerMethodField()
    price           = serializers.SerializerMethodField()
    currency        = serializers.SerializerMethodField()
    delivery_hours  = serializers.SerializerMethodField()
    pitch           = serializers.CharField(source="message", read_only=True)
    responded_at    = serializers.DateTimeField(source="reviewed_at", read_only=True)
    rejection_reason = serializers.SerializerMethodField()

    class Meta:
        model = OrderInterest
        fields = [
            "id", "order_id", "order_topic",
            "writer_id", "writer_username", "writer_rating",
            "price", "currency", "delivery_hours",
            "pitch", "status", "created_at", "responded_at", "rejection_reason",
        ]

    def get_order_topic(self, obj: OrderInterest) -> str:
        order = obj.order
        topic = getattr(order, "topic", None) or getattr(order, "title", None)
        if not topic:
            instructions = getattr(order, "instructions", None) or ""
            topic = instructions[:80] if instructions else f"Order #{order.pk}"
        return topic

    def get_writer_username(self, obj: OrderInterest) -> str:
        w = obj.writer
        return w.get_full_name() or w.email.split("@")[0]

    def get_writer_rating(self, obj: OrderInterest) -> float | None:
        try:
            return getattr(obj.writer, "writer_profile", None) and \
                getattr(obj.writer.writer_profile, "rating", None)
        except Exception:
            return None

    def get_price(self, obj: OrderInterest) -> str:
        return str(obj.metadata.get("price", "0.00"))

    def get_currency(self, obj: OrderInterest) -> str:
        return obj.metadata.get("currency", "USD")

    def get_delivery_hours(self, obj: OrderInterest) -> int:
        return int(obj.metadata.get("delivery_hours", 0))

    def get_rejection_reason(self, obj: OrderInterest) -> str | None:
        return obj.metadata.get("rejection_reason") or None


class WriterBidSubmitView(GenericAPIView):
    """
    POST /api/v1/orders/orders/<order_id>/bids/

    Writer submits a bid on a pool-visible order.
    Internally creates an OrderInterest; price and delivery_hours are
    stored in metadata so the bid serializer can surface them.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int, *args: Any, **kwargs: Any) -> Response:
        from orders.models import Order
        from orders.services.order_staffing_service import OrderStaffingService
        from django.shortcuts import get_object_or_404

        order = get_object_or_404(Order, pk=order_id, website=getattr(request, "website", None))

        pitch = (request.data.get("pitch") or request.data.get("message") or "").strip()
        price = str(request.data.get("price") or "0.00")
        delivery_hours = int(request.data.get("delivery_hours") or 0)

        try:
            interest = OrderStaffingService.express_interest(
                order=order,
                writer=request.user,
                message=pitch,
                triggered_by=request.user,
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Persist bid-specific metadata (price / delivery offer)
        if price or delivery_hours:
            interest.metadata = {
                **(interest.metadata or {}),
                "price": price,
                "delivery_hours": delivery_hours,
            }
            interest.save(update_fields=["metadata", "updated_at"])

        return Response(
            BidSerializer(interest).data,
            status=status.HTTP_201_CREATED,
        )


class WriterMyBidsView(GenericAPIView):
    """
    GET /api/v1/bids/my/
    List the authenticated writer's own bid (interest) records.
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        qs = (
            OrderInterest.objects
            .filter(writer=request.user)
            .select_related("order", "writer")
            .order_by("-created_at")
        )
        # Optional status filter
        status_param = request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class AdminBidsListView(GenericAPIView):
    """
    GET /api/v1/bids/
    List all bids (staff only).
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if not (request.user.is_staff or getattr(request.user, "role", None) in {"admin", "superadmin"}):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        qs = (
            OrderInterest.objects
            .select_related("order", "writer")
            .order_by("-created_at")
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(qs, many=True).data)


class BidWithdrawView(GenericAPIView):
    """
    POST /api/v1/bids/<interest_id>/withdraw/
    Writer withdraws a bid they submitted.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, interest_id: int, *args: Any, **kwargs: Any) -> Response:
        try:
            interest = OrderInterest.objects.get(
                pk=interest_id,
                writer=request.user,
            )
        except OrderInterest.DoesNotExist:
            return Response({"detail": "Bid not found."}, status=status.HTTP_404_NOT_FOUND)

        if interest.status != OrderInterestStatus.PENDING:
            return Response(
                {"detail": "Only pending bids can be withdrawn."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        interest.status = OrderInterestStatus.WITHDRAWN
        from django.utils import timezone
        interest.withdrawn_at = timezone.now()
        interest.save(update_fields=["status", "withdrawn_at", "updated_at"])

        return Response({"detail": "Bid withdrawn."})

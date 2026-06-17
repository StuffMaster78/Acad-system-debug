"""
Admin/superadmin endpoints for managing order number sequences.

GET    /orders/number-sequences/          — list all sequences for this website
POST   /orders/number-sequences/          — create a new sequence
GET    /orders/number-sequences/<id>/     — retrieve a sequence
POST   /orders/number-sequences/<id>/deactivate/ — deactivate a sequence
"""
from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from class_management.models import ClassOrder
from orders.models.orders.order_number_sequence import (
    OrderNumberScope,
    OrderNumberSequence,
)
from orders.models import Order
from orders.services.order_number_service import OrderNumberService
from special_orders.models import SpecialOrder


def _serialize(seq: OrderNumberSequence) -> dict[str, Any]:
    return {
        "id": seq.pk,
        "scope": seq.scope,
        "period": seq.period,
        "prefix": seq.prefix,
        "seed": seq.seed,
        "padding": seq.padding,
        "next_number": seq.next_number,
        "is_active": seq.is_active,
        "created_at": seq.created_at.isoformat(),
        "updated_at": seq.updated_at.isoformat(),
        "created_by_id": seq.created_by_id,
        "example": seq.format_number(seq.next_number),
    }


class OrderNumberSequenceListCreateView(APIView):
    """List all sequences and create new ones."""

    permission_classes = [permissions.IsAuthenticated]

    def _require_admin(self, request: Request) -> bool:
        role = getattr(request.user, "role", None)
        return role in {"admin", "superadmin"}

    def get(self, request: Request) -> Response:
        if not self._require_admin(request):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)
        website = getattr(request, "website", None)
        if not website:
            return Response({"detail": "Website context required."}, status=status.HTTP_400_BAD_REQUEST)
        qs = OrderNumberSequence.objects.filter(website=website).order_by("-created_at")
        return Response([_serialize(s) for s in qs], status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        if not self._require_admin(request):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)
        website = getattr(request, "website", None)
        if not website:
            return Response({"detail": "Website context required."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        seed = data.get("seed")
        if seed is None:
            return Response({"detail": "seed is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            seq = OrderNumberService.create_sequence(
                website=website,
                scope=data.get("scope", OrderNumberScope.NORMAL_ORDER),
                period=data.get("period") or None,
                seed=int(seed),
                prefix=data.get("prefix", ""),
                padding=int(data.get("padding", 5)),
                created_by=request.user,
            )
        except (ValidationError, ValueError) as exc:
            detail = str(exc.message if hasattr(exc, "message") else exc)
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_serialize(seq), status=status.HTTP_201_CREATED)


class OrderNumberSequenceDetailView(APIView):
    """Retrieve or deactivate a single sequence."""

    permission_classes = [permissions.IsAuthenticated]

    def _require_admin(self, request: Request) -> bool:
        role = getattr(request.user, "role", None)
        return role in {"admin", "superadmin"}

    def _get_seq(self, request: Request, pk: int) -> OrderNumberSequence:
        website = getattr(request, "website", None)
        return get_object_or_404(OrderNumberSequence, pk=pk, website=website)

    def get(self, request: Request, pk: int) -> Response:
        if not self._require_admin(request):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)
        seq = self._get_seq(request, pk)
        return Response(_serialize(seq), status=status.HTTP_200_OK)

    def post(self, request: Request, pk: int) -> Response:
        """POST to /deactivate/ sub-path."""
        if not self._require_admin(request):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)
        seq = self._get_seq(request, pk)
        OrderNumberService.deactivate_sequence(seq)
        return Response(_serialize(seq), status=status.HTTP_200_OK)


class WorkReferenceLookupView(APIView):
    """Find normal, class, or special orders by public reference."""

    permission_classes = [permissions.IsAuthenticated]

    STAFF_ROLES = {"admin", "superadmin", "support", "editor"}

    def get(self, request: Request, reference: str) -> Response:
        if getattr(request.user, "role", None) not in self.STAFF_ROLES:
            return Response({"detail": "Staff only."}, status=status.HTTP_403_FORBIDDEN)

        ref = reference.strip()
        if not ref:
            return Response({"detail": "reference is required."}, status=status.HTTP_400_BAD_REQUEST)

        website = getattr(request, "website", None)
        include_all_websites = getattr(request.user, "role", None) == "superadmin"

        matches = [
            *self._normal_order_matches(ref=ref, website=website, all_websites=include_all_websites),
            *self._class_order_matches(ref=ref, website=website, all_websites=include_all_websites),
            *self._special_order_matches(ref=ref, website=website, all_websites=include_all_websites),
        ]

        return Response(
            {
                "reference": ref,
                "count": len(matches),
                "matches": matches,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _scope_queryset(qs, *, website, all_websites: bool):
        if all_websites or website is None:
            return qs
        return qs.filter(website=website)

    @classmethod
    def _normal_order_matches(cls, *, ref: str, website, all_websites: bool) -> list[dict[str, Any]]:
        query = Q(public_order_number__iexact=ref)
        if ref.isdigit():
            query |= Q(pk=int(ref))
        qs = cls._scope_queryset(Order.objects.filter(query), website=website, all_websites=all_websites)
        return [
            {
                "kind": "normal_order",
                "id": order.pk,
                "reference": order.reference,
                "title": order.topic,
                "status": order.status,
                "website_id": order.website_id,
                "client_id": order.client_id,
                "writer_id": order.assigned_writer_id,
                "created_at": order.created_at.isoformat() if order.created_at else None,
            }
            for order in qs[:10]
        ]

    @classmethod
    def _class_order_matches(cls, *, ref: str, website, all_websites: bool) -> list[dict[str, Any]]:
        query = Q(public_order_number__iexact=ref)
        if ref.isdigit():
            query |= Q(pk=int(ref))
        qs = cls._scope_queryset(ClassOrder.objects.filter(query), website=website, all_websites=all_websites)
        return [
            {
                "kind": "class_order",
                "id": class_order.pk,
                "reference": class_order.reference,
                "title": class_order.title,
                "status": class_order.status,
                "website_id": class_order.website_id,
                "client_id": class_order.client_id,
                "writer_id": class_order.assigned_writer_id,
                "created_at": class_order.created_at.isoformat() if class_order.created_at else None,
            }
            for class_order in qs[:10]
        ]

    @classmethod
    def _special_order_matches(cls, *, ref: str, website, all_websites: bool) -> list[dict[str, Any]]:
        query = Q(public_order_number__iexact=ref)
        if ref.isdigit():
            query |= Q(pk=int(ref))
        qs = cls._scope_queryset(SpecialOrder.objects.filter(query), website=website, all_websites=all_websites)
        return [
            {
                "kind": "special_order",
                "id": special_order.pk,
                "reference": special_order.reference,
                "title": special_order.title,
                "status": special_order.status,
                "website_id": special_order.website_id,
                "client_id": special_order.client_id,
                "writer_id": special_order.writer_id,
                "created_at": special_order.created_at.isoformat() if special_order.created_at else None,
            }
            for special_order in qs[:10]
        ]

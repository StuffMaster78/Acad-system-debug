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
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models.orders.order_number_sequence import (
    OrderNumberScope,
    OrderNumberSequence,
)
from orders.services.order_number_service import OrderNumberService


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

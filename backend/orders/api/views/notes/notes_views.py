from __future__ import annotations

from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.models import Order, OrderOperationalNote


def _serialize_note(note: OrderOperationalNote) -> dict:
    return {
        "id": note.pk,
        "author_id": note.author_id,
        "author_username": getattr(note.author, "username", None) if note.author_id else None,
        "body": note.body,
        "is_pinned": note.is_pinned,
        "created_at": note.created_at.isoformat() if note.created_at else None,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
    }


class OrderNotesView(GenericAPIView):
    """
    List and create operational notes for an order.

    Staff-only. Notes are never exposed to clients or writers.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        user = request.user
        order = get_object_or_404(Order, pk=order_id, website=user.website) # type: ignore[attr-defined]
        notes = (
            OrderOperationalNote.objects.filter(order=order)
            .select_related("author")
            .order_by("-is_pinned", "-created_at")
        )
        return Response([_serialize_note(n) for n in notes])

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        user = request.user
        order = get_object_or_404(Order, pk=order_id, website=user.website) # type: ignore[attr-defined]
        body = str(request.data.get("body", "")).strip()
        if not body:
            return Response({"detail": "body is required."}, status=status.HTTP_400_BAD_REQUEST)
        note = OrderOperationalNote.objects.create(
            website=order.website,
            order=order,
            author=user,
            body=body,
        )
        note.refresh_from_db()
        note.author = user # avoid extra query
        return Response(_serialize_note(note), status=status.HTTP_201_CREATED)


class OrderNoteDetailView(GenericAPIView):
    """
    Pin/unpin or delete a single operational note.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(
        self,
        request: Request,
        order_id: int,
        note_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        user = request.user
        note = get_object_or_404(
            OrderOperationalNote,
            pk=note_id,
            order_id=order_id,
            website=user.website, # type: ignore[attr-defined]
        )
        if "is_pinned" in request.data:
            note.is_pinned = bool(request.data["is_pinned"])
            note.save(update_fields=["is_pinned", "updated_at"])
        note.refresh_from_db()
        return Response(_serialize_note(note))

    def delete(
        self,
        request: Request,
        order_id: int,
        note_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        user = request.user
        note = get_object_or_404(
            OrderOperationalNote,
            pk=note_id,
            order_id=order_id,
            website=user.website, # type: ignore[attr-defined]
        )
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

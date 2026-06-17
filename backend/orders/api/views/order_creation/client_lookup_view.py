"""
GET /orders/client-lookup/?q=<email_or_id>

Staff/admin-only endpoint to resolve a client by email address or
numeric ID before creating an order on their behalf.

Returns the minimal client profile needed to populate a "creating for"
indicator in the admin order form.
"""
from __future__ import annotations

from typing import Any, cast

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.api.permissions.order_creation_permissions import CanCreateOrderOnBehalf


User = get_user_model()


class ClientLookupView(APIView):
    """
    Resolve a client by email or numeric ID — staff only.

    GET /orders/client-lookup/?q=jane@example.com
    GET /orders/client-lookup/?q=123

    Returns a single client object or 404.  Scoped to the requesting
    user's website so cross-tenant lookups are impossible.
    """

    permission_classes = [permissions.IsAuthenticated, CanCreateOrderOnBehalf]

    def get(self, request: Request) -> Response:
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response(
                {"detail": "q is required (email or client ID)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = User.objects.filter(website=website)

        # Try numeric ID first, then fall back to email substring search
        if q.isdigit():
            qs = qs.filter(pk=int(q))
        else:
            qs = qs.filter(
                Q(email__iexact=q) | Q(email__icontains=q)
            ).exclude(role__in=["writer", "staff", "admin", "superadmin"])

        # Cap results so this never becomes a full user dump
        results = qs.order_by("email")[:10]

        data = [
            {
                "id": u.pk,
                "email": u.email,
                "username": u.username,
                "full_name": u.get_full_name() if hasattr(u, "get_full_name") else "",
                "role": getattr(u, "role", None),
                "is_active": u.is_active,
            }
            for u in results
        ]

        if not data:
            return Response(
                {"detail": f"No client found matching '{q}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(data, status=status.HTTP_200_OK)

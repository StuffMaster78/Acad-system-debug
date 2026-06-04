from __future__ import annotations

from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChangelogEntry


class ChangelogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangelogEntry
        fields = [
            "id", "portal_surface", "entry_type", "version",
            "title", "body", "is_pinned", "published_at",
        ]
        read_only_fields = fields


class ChangelogListView(APIView):
    """
    GET /api/v1/changelog/?surface=client&website=3
    Returns published entries for the given portal surface.
    Tenant resolution uses request.website (set by middleware) if no
    explicit website param is provided.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        surface = request.query_params.get("surface", "public")
        website_id = request.query_params.get("website")

        qs = ChangelogEntry.objects.filter(is_published=True)

        if surface != "public":
            qs = qs.filter(portal_surface__in=[surface, "public"])

        # Website scoping: explicit param > request.website > global (null)
        website = getattr(request, "website", None)
        if website_id:
            qs = qs.filter(website_id=website_id)
        elif website:
            qs = qs.filter(website__in=[website, None])  # type: ignore[list-item]
        else:
            qs = qs.filter(website__isnull=True)

        limit = min(int(request.query_params.get("limit", 20)), 100)
        entries = qs[:limit]

        return Response(ChangelogEntrySerializer(entries, many=True).data)

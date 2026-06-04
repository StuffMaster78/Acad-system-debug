from __future__ import annotations

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SavedView


class SavedViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedView
        fields = ["id", "view_type", "name", "filters", "is_default", "created_at"]
        read_only_fields = ["id", "created_at"]


class SavedViewListView(APIView):
    """
    GET  /api/v1/saved-views/?view_type=orders  — list presets for a view type
    POST /api/v1/saved-views/                    — create a new preset
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = SavedView.objects.filter(user=request.user)
        view_type = request.query_params.get("view_type")
        if view_type:
            qs = qs.filter(view_type=view_type)
        return Response(SavedViewSerializer(qs, many=True).data)

    def post(self, request):
        serializer = SavedViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["name"]
        view_type = serializer.validated_data["view_type"]

        # If is_default, clear other defaults for this view_type
        if serializer.validated_data.get("is_default"):
            SavedView.objects.filter(user=request.user, view_type=view_type).update(is_default=False)

        saved, _ = SavedView.objects.update_or_create(
            user=request.user,
            view_type=view_type,
            name=name,
            defaults={
                "filters": serializer.validated_data.get("filters", {}),
                "is_default": serializer.validated_data.get("is_default", False),
                "website": getattr(request, "website", None),
            },
        )
        return Response(
            SavedViewSerializer(saved).data,
            status=status.HTTP_201_CREATED if _ else status.HTTP_200_OK,
        )


class SavedViewDetailView(APIView):
    """
    DELETE /api/v1/saved-views/{id}/  — delete a preset
    PATCH  /api/v1/saved-views/{id}/  — rename or update filters
    """

    permission_classes = [IsAuthenticated]

    def _get(self, request, pk: int):
        try:
            return SavedView.objects.get(pk=pk, user=request.user)
        except SavedView.DoesNotExist:
            return None

    def patch(self, request, pk: int):
        sv = self._get(request, pk)
        if sv is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SavedViewSerializer(sv, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get("is_default"):
            SavedView.objects.filter(user=request.user, view_type=sv.view_type).exclude(pk=sv.pk).update(is_default=False)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk: int):
        sv = self._get(request, pk)
        if sv is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        sv.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

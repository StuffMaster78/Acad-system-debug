from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from class_management.api.serializers.class_config_serializers import (
    ClassServiceConfigSerializer,
)
from class_management.models import ClassServiceConfig
from websites.models.websites import Website


class ClassServiceConfigListView(APIView):
    """
    List active class service configs for the resolved tenant website.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def _can_manage(user) -> bool:
        role = getattr(user, "role", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or role in {"superadmin", "admin"})
        )

    def _website(self, request):
        requested_website_id = request.query_params.get("website_id")
        role = getattr(request.user, "role", None)
        if requested_website_id and (
            request.user.is_superuser or role == "superadmin"
        ):
            website = Website.objects.filter(pk=requested_website_id).first()
            if website is None:
                raise NotFound("Website not found.")
            return website

        return getattr(request, "website", None) or getattr(
            request.user,
            "website",
            None,
        )

    def get(self, request):
        website = self._website(request)
        queryset = ClassServiceConfig.objects.none()
        if website is not None:
            queryset = ClassServiceConfig.objects.filter(
                website=website,
                is_active=True,
            ).order_by("display_order", "name")

        serializer = ClassServiceConfigSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not self._can_manage(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        website = self._website(request)
        serializer = ClassServiceConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        config = serializer.save(
            website=website,
            created_by=request.user,
        )
        return Response(
            ClassServiceConfigSerializer(config).data,
            status=status.HTTP_201_CREATED,
        )


class ClassServiceConfigDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _can_manage(user) -> bool:
        role = getattr(user, "role", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or role in {"superadmin", "admin"})
        )

    def _get_config(self, request, pk: int):
        website = getattr(request, "website", None) or getattr(
            request.user,
            "website",
            None,
        )
        qs = ClassServiceConfig.objects.filter(pk=pk)
        if not (request.user.is_superuser or getattr(request.user, "role", None) == "superadmin"):
            qs = qs.filter(website=website)
        return qs.first()

    def get(self, request, pk: int):
        config = self._get_config(request, pk)
        if config is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClassServiceConfigSerializer(config).data)

    def patch(self, request, pk: int):
        if not self._can_manage(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        config = self._get_config(request, pk)
        if config is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassServiceConfigSerializer(
            config,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

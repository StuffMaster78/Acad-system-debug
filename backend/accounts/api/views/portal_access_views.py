from __future__ import annotations

from rest_framework import viewsets

from accounts.api.serializers.portal_access_serializers import (
    PortalAccessSerializer,
    PortalDefinitionSerializer,
)
from accounts.models import PortalAccess, PortalDefinition
from core.permissions.base import BasePlatformPermission


class ManagePortalAccessPermission(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "accounts.assign_roles"
    require_tenant = False


class PortalDefinitionViewSet(viewsets.ModelViewSet):
    queryset = PortalDefinition.objects.all().order_by("code")
    serializer_class = PortalDefinitionSerializer
    permission_classes = [ManagePortalAccessPermission]


class PortalAccessViewSet(viewsets.ModelViewSet):
    queryset = PortalAccess.objects.select_related(
        "user",
        "portal",
        "granted_by",
    ).order_by("-created_at")
    serializer_class = PortalAccessSerializer
    permission_classes = [ManagePortalAccessPermission]
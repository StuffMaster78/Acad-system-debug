from __future__ import annotations

from rest_framework import viewsets

from accounts.api.serializers.permission_serializers import (
    PermissionDefinitionSerializer,
    RolePermissionSerializer,
)
from accounts.models import PermissionDefinition, RolePermission
from core.permissions.base import BasePlatformPermission


class ManagePermissionsPermission(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "accounts.assign_roles"
    require_tenant = False


class PermissionDefinitionViewSet(viewsets.ModelViewSet):
    queryset = PermissionDefinition.objects.all().order_by("code")
    serializer_class = PermissionDefinitionSerializer
    permission_classes = [ManagePermissionsPermission]


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.select_related(
        "role",
        "permission",
    ).order_by("role__label", "permission__code")
    serializer_class = RolePermissionSerializer
    permission_classes = [ManagePermissionsPermission]
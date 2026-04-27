from __future__ import annotations

from rest_framework import viewsets

from accounts.api.serializers.tenant_access_serializers import (
    TenantAccessSerializer,
)
from accounts.models import TenantAccess
from core.permissions.base import BasePlatformPermission


class ManageTenantAccessPermission(BasePlatformPermission):
    required_portal = "internal_admin"
    required_permission = "accounts.assign_roles"
    require_tenant = False


class TenantAccessViewSet(viewsets.ModelViewSet):
    queryset = TenantAccess.objects.select_related(
        "user",
        "website",
        "granted_by",
    ).order_by("-created_at")
    serializer_class = TenantAccessSerializer
    permission_classes = [ManageTenantAccessPermission]
from typing import Any, NotRequired, TypedDict, cast

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers.account_role_serializer import (
    AccountRoleSerializer,
)
from accounts.api.serializers.role_assignment_serializer import (
    AssignRoleSerializer,
    RevokeRoleSerializer,
)
from accounts.permissions import IsAdminOrSuperAdminRole
from accounts.selectors.account_role_selector import AccountRoleSelector
from accounts.selectors.account_selector import AccountSelector
from accounts.services.account_role_service import AccountRoleService


class AssignRoleData(TypedDict):
    """Typed payload for role assignment requests."""

    role_key: str
    metadata: NotRequired[dict[str, Any]]


class RevokeRoleData(TypedDict):
    """Typed payload for role revocation requests."""

    role_key: str
    metadata: NotRequired[dict[str, Any]]


class ListMyAccountRolesView(APIView):
    """Return active roles for the current website account."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """List active roles for the current account profile."""
        profile = AccountSelector.get_account_profile(
            website=request.website,
            user=request.user,
        )
        roles = AccountRoleSelector.get_active_roles(
            account_profile=profile,
        )
        response_serializer = AccountRoleSerializer(roles, many=True)
        return Response(response_serializer.data)


class AssignAccountRoleView(APIView):
    """Assign a role to an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def post(self, request, account_profile_id, *args, **kwargs):
        """Assign a role to the given account profile."""
        request_serializer = AssignRoleSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = cast(AssignRoleData, request_serializer.validated_data)

        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )

        assigned_role = AccountRoleService.assign_role_by_key(
            account_profile=profile,
            role_key=data["role_key"],
            actor=request.user,
            metadata=data.get("metadata"),
        )

        response_serializer = AccountRoleSerializer(assigned_role)
        return Response(response_serializer.data)


class RevokeAccountRoleView(APIView):
    """Revoke a role from an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def post(self, request, account_profile_id, *args, **kwargs):
        """Revoke a role from the given account profile."""
        request_serializer = RevokeRoleSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = cast(RevokeRoleData, request_serializer.validated_data)

        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )

        revoked_role = AccountRoleService.revoke_role_by_key(
            account_profile=profile,
            role_key=data["role_key"],
            actor=request.user,
            metadata=data.get("metadata"),
        )

        response_serializer = AccountRoleSerializer(revoked_role)
        return Response(response_serializer.data)
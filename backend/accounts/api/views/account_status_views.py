from typing import Any, NotRequired, TypedDict, cast

from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers.account_profile_serializer import (
    AccountProfileSerializer,
)
from accounts.api.serializers.account_status_serializer import (
    ActivateAccountSerializer,
    ReactivateAccountSerializer,
    SuspendAccountSerializer,
)
from accounts.permissions import IsAdminOrSuperAdminRole
from accounts.selectors.account_selector import AccountSelector
from accounts.services.account_activation_service import (
    AccountActivationService,
)


class ActivateAccountData(TypedDict):
    """Typed payload for account activation requests."""

    reason: str
    metadata: NotRequired[dict[str, Any]]


class SuspendAccountData(TypedDict):
    """Typed payload for account suspension requests."""

    reason: str
    metadata: NotRequired[dict[str, Any]]


class ReactivateAccountData(TypedDict):
    """Typed payload for account reactivation requests."""

    reason: str
    metadata: NotRequired[dict[str, Any]]


class ActivateAccountView(APIView):
    """Activate an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def post(self, request, account_profile_id, *args, **kwargs):
        """Activate the target account profile."""
        request_serializer = ActivateAccountSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = cast(ActivateAccountData, request_serializer.validated_data)

        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )

        updated_profile = AccountActivationService.activate_account(
            account_profile=profile,
            actor=request.user,
            reason=data["reason"],
            metadata=data.get("metadata"),
        )

        response_serializer = AccountProfileSerializer(updated_profile)
        return Response(response_serializer.data)


class SuspendAccountView(APIView):
    """Suspend an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def post(self, request, account_profile_id, *args, **kwargs):
        """Suspend the target account profile."""
        request_serializer = SuspendAccountSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = cast(SuspendAccountData, request_serializer.validated_data)

        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )

        updated_profile = AccountActivationService.suspend_account(
            account_profile=profile,
            actor=request.user,
            reason=data["reason"],
            metadata=data.get("metadata"),
        )

        response_serializer = AccountProfileSerializer(updated_profile)
        return Response(response_serializer.data)


class ReactivateAccountView(APIView):
    """Reactivate an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def post(self, request, account_profile_id, *args, **kwargs):
        """Reactivate the target account profile."""
        request_serializer = ReactivateAccountSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = cast(ReactivateAccountData, request_serializer.validated_data)

        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )

        updated_profile = AccountActivationService.reactivate_account(
            account_profile=profile,
            actor=request.user,
            reason=data["reason"],
            metadata=data.get("metadata"),
        )

        response_serializer = AccountProfileSerializer(updated_profile)
        return Response(response_serializer.data)
from typing import Any, NotRequired, TypedDict, cast

from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers.account_profile_serializer import (
    AccountProfileSerializer,
)
from accounts.api.serializers.onboarding_action_serializer import (
    ClientOnboardingSerializer,
    StaffOnboardingSerializer,
    WriterOnboardingSerializer,
)
from accounts.permissions import IsAdminOrSuperAdminRole
from accounts.selectors.account_selector import AccountSelector
from accounts.services.client_onboarding_service import (
    ClientOnboardingService,
)
from accounts.services.staff_onboarding_service import (
    StaffOnboardingService,
)
from accounts.services.writer_onboarding_service import (
    WriterOnboardingService,
)


class ClientOnboardingData(TypedDict):
    """Typed payload for client onboarding requests."""

    metadata: NotRequired[dict[str, Any]]


class WriterOnboardingData(TypedDict):
    """Typed payload for writer onboarding requests."""

    require_review: bool
    metadata: NotRequired[dict[str, Any]]


class StaffOnboardingData(TypedDict):
    """Typed payload for staff onboarding requests."""

    role_keys: list[str]
    metadata: NotRequired[dict[str, Any]]


class CompleteClientOnboardingView(APIView):
    """Complete client onboarding for an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def post(self, request, account_profile_id, *args, **kwargs):
        """Complete client onboarding."""
        request_serializer = ClientOnboardingSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = cast(ClientOnboardingData, request_serializer.validated_data)

        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )

        updated_profile = ClientOnboardingService.complete_onboarding(
            account_profile=profile,
            actor=request.user,
            metadata=data.get("metadata"),
        )

        response_serializer = AccountProfileSerializer(updated_profile)
        return Response(response_serializer.data)


class CompleteWriterOnboardingView(APIView):
    """Complete writer onboarding for an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def post(self, request, account_profile_id, *args, **kwargs):
        """Complete writer onboarding."""
        request_serializer = WriterOnboardingSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = cast(WriterOnboardingData, request_serializer.validated_data)

        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )

        updated_profile = WriterOnboardingService.complete_onboarding(
            account_profile=profile,
            actor=request.user,
            metadata=data.get("metadata"),
            require_review=data["require_review"],
        )

        response_serializer = AccountProfileSerializer(updated_profile)
        return Response(response_serializer.data)


class CompleteStaffOnboardingView(APIView):
    """Complete staff onboarding for an account profile."""

    permission_classes = [IsAdminOrSuperAdminRole]

    def post(self, request, account_profile_id, *args, **kwargs):
        """Complete staff onboarding."""
        request_serializer = StaffOnboardingSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        data = cast(StaffOnboardingData, request_serializer.validated_data)

        profile = AccountSelector.get_account_profile_by_id(
            website=request.website,
            account_profile_id=account_profile_id,
        )

        updated_profile = StaffOnboardingService.complete_onboarding(
            account_profile=profile,
            role_keys=data["role_keys"],
            actor=request.user,
            metadata=data.get("metadata"),
        )

        response_serializer = AccountProfileSerializer(updated_profile)
        return Response(response_serializer.data)
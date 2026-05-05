from __future__ import annotations

from typing import Any, cast

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanCreateOwnSensitiveAccess,
    CanManageSensitiveAccess,
    CanManageTwoFactorRequest,
    CanRevealSensitiveAccess,
    CanViewSensitiveAccessLogs,
)
from special_orders.api.serializers.sensitive_access_serializers import (
    AccessGrantSerializer,
    AccessLogSerializer,
    CompleteTwoFactorRequestSerializer,
    CreateExternalLinkSerializer,
    CreateTwoFactorRequestSerializer,
    CreateVaultSerializer,
    ExternalLinkSerializer,
    GrantAccessSerializer,
    InstitutionProfileSerializer,
    RevealVaultSerializer,
    TwoFactorRequestSerializer,
    UpsertInstitutionProfileSerializer,
    VaultRevealSerializer,
    VaultSafeSerializer,
)
from special_orders.selectors import (
    SpecialOrderSelector,
    SpecialOrderSensitiveAccessSelector,
)
from special_orders.services.new_services.special_order_sensitive_access_service import (
    SpecialOrderSensitiveAccessService,
)


class UpsertInstitutionProfileView(APIView):
    permission_classes = [IsAuthenticated, CanCreateOwnSensitiveAccess]

    def post(self, request, special_order_id: int):
        serializer = UpsertInstitutionProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )

        profile = (
            SpecialOrderSensitiveAccessService
            .create_or_update_institution_profile(
                special_order=special_order,
                institution_name=str(data["institution_name"]),
                institution_type=str(data["institution_type"]),
                country=str(data.get("country", "")),
                state_region=str(data.get("state_region", "")),
                city=str(data.get("city", "")),
                program_name=str(data.get("program_name", "")),
                course_code=str(data.get("course_code", "")),
                course_name=str(data.get("course_name", "")),
                instructor_name=str(data.get("instructor_name", "")),
                term_or_semester=str(data.get("term_or_semester", "")),
                metadata=cast(
                    dict[str, Any],
                    data.get("metadata", {}),
                ),
            )
        )

        return Response(InstitutionProfileSerializer(profile).data)


class CreateVaultView(APIView):
    permission_classes = [IsAuthenticated, CanCreateOwnSensitiveAccess]

    def post(self, request, special_order_id: int):
        serializer = CreateVaultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )

        vault = SpecialOrderSensitiveAccessService.create_vault(
            special_order=special_order,
            platform=str(data["platform"]),
            created_by=request.user,
            platform_label=str(data.get("platform_label", "")),
            login_url=str(data.get("login_url", "")),
            username=str(data.get("username", "")),
            encrypted_password=str(data.get("encrypted_password", "")),
            recovery_email=str(data.get("recovery_email", "")),
            recovery_phone_last4=str(
                data.get("recovery_phone_last4", "")
            ),
            access_notes=str(data.get("access_notes", "")),
            requires_2fa=bool(data.get("requires_2fa", False)),
            preferred_2fa_method=str(
                data.get("preferred_2fa_method", "")
            ),
            preferred_2fa_window_start=data.get(
                "preferred_2fa_window_start"
            ),
            preferred_2fa_window_end=data.get(
                "preferred_2fa_window_end"
            ),
            timezone_name=str(data.get("timezone_name", "UTC")),
            metadata=cast(dict[str, Any], data.get("metadata", {})),
            request=request,
        )

        return Response(
            VaultSafeSerializer(vault).data,
            status=status.HTTP_201_CREATED,
        )


class ListVaultsView(APIView):
    permission_classes = [IsAuthenticated, CanRevealSensitiveAccess]

    def get(self, request, special_order_id: int):
        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )

        vaults = SpecialOrderSensitiveAccessSelector.list_vaults(
            website=request.user.website,
            special_order=special_order,
        )

        serializer = VaultSafeSerializer(vaults, many=True)
        return Response(serializer.data)


class RevealVaultView(APIView):
    permission_classes = [IsAuthenticated, CanRevealSensitiveAccess]

    def post(self, request, vault_id: int):
        serializer = RevealVaultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        vault = SpecialOrderSensitiveAccessSelector.get_vault(
            website=request.user.website,
            vault_id=vault_id,
        )
        self.check_object_permissions(request, vault)

        revealed_vault = SpecialOrderSensitiveAccessService.reveal_vault(
            vault=vault,
            actor=request.user,
            access_level=str(data["access_level"]),
            request=request,
        )

        return Response(VaultRevealSerializer(revealed_vault).data)


class CreateExternalLinkView(APIView):
    permission_classes = [IsAuthenticated, CanCreateOwnSensitiveAccess]

    def post(self, request, special_order_id: int):
        serializer = CreateExternalLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )

        link = SpecialOrderSensitiveAccessService.create_external_link(
            special_order=special_order,
            label=str(data["label"]),
            url=str(data["url"]),
            created_by=request.user,
            link_type=str(data.get("link_type", "other")),
            requires_login=bool(data.get("requires_login", False)),
            notes=str(data.get("notes", "")),
        )

        return Response(
            ExternalLinkSerializer(link).data,
            status=status.HTTP_201_CREATED,
        )


class GrantVaultAccessView(APIView):
    permission_classes = [IsAuthenticated, CanManageSensitiveAccess]

    def post(self, request, vault_id: int):
        serializer = GrantAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        vault = SpecialOrderSensitiveAccessSelector.get_vault(
            website=request.user.website,
            vault_id=vault_id,
        )
        self.check_object_permissions(request, vault)

        User = get_user_model()
        granted_to = User.objects.get(
            id=int(data["granted_to_id"]),
            website=request.user.website,
        )

        grant = SpecialOrderSensitiveAccessService.grant_access(
            vault=vault,
            granted_to=granted_to,
            granted_by=request.user,
            access_level=str(data["access_level"]),
            reason=str(data["reason"]),
            expires_at=data.get("expires_at"),
            request=request,
        )

        return Response(
            AccessGrantSerializer(grant).data,
            status=status.HTTP_201_CREATED,
        )


class RevokeVaultAccessView(APIView):
    permission_classes = [IsAuthenticated, CanManageSensitiveAccess]

    def post(self, request, grant_id: int):
        grant = SpecialOrderSensitiveAccessSelector.get_grant(
            website=request.user.website,
            grant_id=grant_id,
        )
        self.check_object_permissions(request, grant)

        grant = SpecialOrderSensitiveAccessService.revoke_access(
            grant=grant,
            revoked_by=request.user,
            request=request,
        )

        return Response(AccessGrantSerializer(grant).data)


class ListVaultAccessLogsView(APIView):
    permission_classes = [IsAuthenticated, CanViewSensitiveAccessLogs]

    def get(self, request, vault_id: int):
        vault = SpecialOrderSensitiveAccessSelector.get_vault(
            website=request.user.website,
            vault_id=vault_id,
        )
        self.check_object_permissions(request, vault)

        logs = SpecialOrderSensitiveAccessSelector.list_access_logs(
            website=request.user.website,
            vault=vault,
        )

        return Response(AccessLogSerializer(logs, many=True).data)


class CreateTwoFactorRequestView(APIView):
    permission_classes = [IsAuthenticated, CanManageTwoFactorRequest]

    def post(self, request, vault_id: int):
        serializer = CreateTwoFactorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        vault = SpecialOrderSensitiveAccessSelector.get_vault(
            website=request.user.website,
            vault_id=vault_id,
        )
        self.check_object_permissions(request, vault)

        two_factor_request = (
            SpecialOrderSensitiveAccessService.request_two_factor_code(
                vault=vault,
                requested_by=request.user,
                message=str(data.get("message", "")),
                requested_for_time=data.get("requested_for_time"),
                expires_at=data.get("expires_at"),
                request=request,
            )
        )

        return Response(
            TwoFactorRequestSerializer(two_factor_request).data,
            status=status.HTTP_201_CREATED,
        )


class CompleteTwoFactorRequestView(APIView):
    permission_classes = [IsAuthenticated, CanManageTwoFactorRequest]

    def post(self, request, request_id: int):
        serializer = CompleteTwoFactorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        two_factor_request = (
            SpecialOrderSensitiveAccessSelector.get_two_factor_request(
                website=request.user.website,
                request_id=request_id,
            )
        )
        self.check_object_permissions(request, two_factor_request)

        two_factor_request = (
            SpecialOrderSensitiveAccessService
            .complete_two_factor_request(
                two_factor_request=two_factor_request,
                completed_by=request.user,
                code_reference=str(data.get("code_reference", "")),
                request=request,
            )
        )

        return Response(TwoFactorRequestSerializer(two_factor_request).data)
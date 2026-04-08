from typing import Any, cast

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.impersonation_serializers import (
    ImpersonationCreateResponseSerializer,
    ImpersonationCreateSerializer,
    ImpersonationEndResponseSerializer,
    ImpersonationEndSerializer,
    ImpersonationStartResponseSerializer,
    ImpersonationStartSerializer,
    ImpersonationStatusResponseSerializer,
)
from authentication.services.impersonation_service import (
    ImpersonationService,
)
from authentication.api.permissions.impersonation_permissions import (
    NotImpersonatingPermission,
)

User = get_user_model()


class ImpersonationCreateTokenView(APIView):
    """
    Create an impersonation token for a target user.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = ImpersonationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = User.objects.filter(
            pk=validated_data["target_user_id"],
            website=website,
        ).first()

        if target_user is None:
            return Response(
                {"detail": "Target user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        _token_obj, raw_token = ImpersonationService.create_token(
            admin_user=request.user,
            target_user=target_user,
            website=website,
            reason=validated_data["reason"],
        )

        response_serializer = ImpersonationCreateResponseSerializer(
            {
                "success": True,
                "token": raw_token,
                "expires_in_hours": ImpersonationService.DEFAULT_EXPIRY_HOURS,
            }
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ImpersonationStartView(APIView):
    """
    Start impersonation using a valid impersonation token.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = ImpersonationStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        website = getattr(request, "website", None)
        service = ImpersonationService(
            request=request,
            website=website,
        )

        result = service.start_impersonation(
            raw_token=validated_data["token"],
            reason=validated_data.get("reason") or None,
        )

        response_serializer = ImpersonationStartResponseSerializer(result)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class ImpersonationEndView(APIView):
    """
    End an active impersonation session.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = ImpersonationEndSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        website = getattr(request, "website", None)
        service = ImpersonationService(
            request=request,
            website=website,
        )

        result = service.end_impersonation(
            close_tab=validated_data.get("close_tab", False),
            reason=validated_data.get("reason") or None,
        )

        response_serializer = ImpersonationEndResponseSerializer(result)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class ImpersonationStatusView(APIView):
    """
    Return current impersonation state.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        service = ImpersonationService(
            request=request,
            website=website,
        )

        payload = {
            "is_impersonating": service.is_impersonating(),
            "impersonator": service.get_impersonator_info(),
        }

        serializer = ImpersonationStatusResponseSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)
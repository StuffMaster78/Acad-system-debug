from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.account_deletion_serializers import (
    AccountDeletionConfirmSerializer,
    AccountDeletionRequestSerializer,
    CancelDeletionSerializer,
    AccountDeletionResponseSerializer,
    AccountDeletionStateSerializer,
)
from authentication.services.account_deletion_service import (
    AccountDeletionService,
)
from authentication.api.permissions.impersonation_permissions import (
    NotImpersonatingPermission,
)


class AccountDeletionRequestView(APIView):
    """
    Create an account deletion request.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = AccountDeletionRequestSerializer(data=request.data)
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

        service = AccountDeletionService(
            user=request.user,
            website=website,
        )
        request_obj = service.request_deletion(
            reason=validated_data.get("reason", ""),
        )

        response_serializer = AccountDeletionResponseSerializer(
            {
                "success": True,
                "request_id": request_obj.pk,
                "status": request_obj.status,
                "message": "Deletion request created successfully.",
            }
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class AccountDeletionConfirmView(APIView):
    """
    Confirm and schedule account deletion.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = AccountDeletionConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        if not validated_data["confirm"]:
            return Response(
                {"detail": "Confirmation required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AccountDeletionService(
            user=request.user,
            website=website,
        )
        active_request = service.get_active_request()
        if active_request is None:
            return Response(
                {"detail": "No active deletion request found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        service.confirm_deletion(request_obj=active_request)
        scheduled_request, _raw_token = service.schedule_deletion(
            request_obj=active_request,
        )

        return Response(
            {
                "success": True,
                "request_id": scheduled_request.pk,
                "status": scheduled_request.status,
            },
            status=status.HTTP_200_OK,
        )


class CancelAccountDeletionView(APIView):
    """
    Cancel scheduled account deletion using undo token.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CancelDeletionSerializer(data=request.data)
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

        user = request.user if request.user.is_authenticated else None
        if user is None:
            return Response(
                {"detail": "Authenticated user required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        service = AccountDeletionService(
            user=user,
            website=website,
        )
        request_obj = service.cancel_scheduled_deletion_by_token(
            raw_token=validated_data["token"],
        )

        return Response(
            {
                "success": True,
                "request_id": request_obj.pk,
                "status": request_obj.status,
            },
            status=status.HTTP_200_OK,
        )
    

class AccountDeletionStateView(APIView):
    """
    Return the current user's active account deletion request, if any.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AccountDeletionService(
            user=request.user,
            website=website,
        )
        request_obj = service.get_active_request()

        if request_obj is None:
            return Response(
                {"detail": "No active deletion request found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AccountDeletionStateSerializer(
            {
                "request_id": request_obj.pk,
                "status": request_obj.status,
                "requested_at": request_obj.requested_at,
                "confirmed_at": request_obj.confirmed_at,
                "scheduled_deletion_at": request_obj.scheduled_deletion_at,
                "retained_until": getattr(
                    request_obj,
                    "retained_until",
                    None,
                ),
                "completed_at": request_obj.completed_at,
                "reason": request_obj.reason,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

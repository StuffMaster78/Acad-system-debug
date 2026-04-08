from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.permissions.impersonation_permissions import (
    NotImpersonatingPermission,
)
from authentication.api.serializers.support_auth_link_serializers import (
    GenerateUserMagicLinkResponseSerializer,
    GenerateUserPasswordResetLinkResponseSerializer,
)
from authentication.services.support_auth_link_service import (
    SupportAuthLinkService,
)

User = get_user_model()


class AdminGenerateUserMagicLinkView(APIView):
    """
    Generate a magic login link for a target user so support/admin can
    copy it into a support flow or user profile.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
        NotImpersonatingPermission,
    ]

    def post(self, request, user_id, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = User.objects.filter(
            pk=user_id,
            website=website,
        ).first()

        if target_user is None:
            return Response(
                {"detail": "Target user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = SupportAuthLinkService.generate_magic_link(
            target_user=target_user,
            website=website,
            created_by=request.user,
        )

        response_serializer = GenerateUserMagicLinkResponseSerializer(
            result
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class AdminGenerateUserPasswordResetLinkView(APIView):
    """
    Generate a password reset link and OTP for a target user so
    support/admin can help recovery workflows.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
        NotImpersonatingPermission,
    ]

    def post(self, request, user_id, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = User.objects.filter(
            pk=user_id,
            website=website,
        ).first()

        if target_user is None:
            return Response(
                {"detail": "Target user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = SupportAuthLinkService.generate_password_reset_link(
            target_user=target_user,
            website=website,
        )

        response_serializer = (
            GenerateUserPasswordResetLinkResponseSerializer(result)
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
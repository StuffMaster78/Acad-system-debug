from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authentication.models import BackupCode
from authentication.serializers import (
    BackupCodeGenerateSerializer,
    BackupCodeVerifySerializer,
    BackupCodeListSerializer
)
from authentication.services.backup_code_service import BackupCodeService


class BackupCodeViewSet(viewsets.ViewSet):
    """
    ViewSet for managing backup codes with multitenancy.
    """
    permission_classes = [IsAuthenticated]

    def get_service(self):
        return BackupCodeService(
            user=self.request.user,
            website=getattr(self.request, "website", None)
        )

    def list(self, request):
        """
        Lists hashed backup codes for the current user.
        """
        codes = BackupCode.objects.filter(
            user=request.user,
            website=request.website
        ).order_by("-created_at")

        serializer = BackupCodeListSerializer(codes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate_codes(self, request):
        """
        Generates new backup codes.
        """
        serializer = BackupCodeGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        count = serializer.validated_data["count"]
        service = self.get_service()
        codes = service.generate_codes(count=count)

        return Response({"backup_codes": codes}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="verify")
    def verify_code(self, request):
        """
        Verifies a submitted backup code.
        """
        serializer = BackupCodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        service = self.get_service()

        try:
            service.validate_code(code)
            return Response({"valid": True})
        except Exception as e:
            return Response(
                {"valid": False, "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
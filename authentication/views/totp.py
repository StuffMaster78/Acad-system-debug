from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from authentication.serializers import (
    TOTPSetupSerializer,
    TOTPVerifySerializer
)


class TOTPViewSet(viewsets.ViewSet):
    """
    ViewSet to handle TOTP setup and verification.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def setup(self, request):
        """
        Generates a new TOTP secret and QR code.
        """
        serializer = TOTPSetupSerializer(data={}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def verify(self, request):
        """
        Verifies a TOTP OTP code and enables 2FA if valid.
        """
        serializer = TOTPVerifySerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
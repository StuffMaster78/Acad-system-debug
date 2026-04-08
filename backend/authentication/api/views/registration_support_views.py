from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.registration_support_serializers import (
    RegistrationResendResponseSerializer,
    RegistrationResendSerializer,
)
from authentication.services.registration_token_service import (
    RegistrationTokenService,
)
from authentication.throttles.registration_throttles import (
    RegistrationResendThrottle
)

class RegistrationResendView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistrationResendThrottle]

    def post(self, request, *args, **kwargs):
        serializer = RegistrationResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = RegistrationTokenService.resend_registration_verification(
            email=validated_data["email"],
            website=website,
        )

        response_serializer = RegistrationResendResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.auth_serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
)
from authentication.services.login_flow_service import LoginFlowService
from authentication.throttles.login_throttles import LoginRateThrottle
# from accounts.services import AccountAccessProvisioningService

class LoginView(APIView):
    """
    Handle user login through the full login flow service.
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )
        website = getattr(request, "website", None)

        # AccountAccessProvisioningService.provision_client(
        #     user=user,
        #     website=website,  # resolved from request.domain
        # )

        
        result = LoginFlowService.login(
            email=validated_data["email"],
            password=validated_data["password"],
            request=request,
            website=website,
        )

        response_serializer = LoginResponseSerializer(result)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
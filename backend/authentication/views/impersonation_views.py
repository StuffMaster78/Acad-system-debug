from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import UserRateThrottle
from django.utils import timezone

from authentication.models.impersonation import ImpersonationToken
from authentication.serializers import (
    ImpersonationTokenSerializer,
    CreateImpersonationTokenSerializer
)
from authentication.services.impersonation_service import ImpersonationService


class ImpersonationTokenThrottle(UserRateThrottle):
    """
    Limits token creation and usage to avoid abuse.
    """
    rate = "5/hour"


class ImpersonationTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and using impersonation tokens.
    """

    queryset = ImpersonationToken.objects.all()
    serializer_class = ImpersonationTokenSerializer
    permission_classes = [IsAdminUser]
    throttle_classes = [ImpersonationTokenThrottle]

    def get_queryset(self):
        """
        Limit to tokens created by current admin.
        """
        return self.queryset.filter(admin_user=self.request.user)

    def get_serializer_class(self):
        """
        Use different serializer for create.
        """
        if self.action == "create_token":
            return CreateImpersonationTokenSerializer
        return ImpersonationTokenSerializer

    @action(detail=False, methods=["post"])
    def create_token(self, request):
        """
        Admin-only endpoint to create an impersonation token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user = serializer.validated_data["target_user"]
        
        # Use ImpersonationService to generate token with permission checks
        from websites.utils import get_current_website
        website = get_current_website(request)
        
        try:
            token_obj = ImpersonationService.generate_token(
                admin_user=request.user,
                target_user=target_user,
                website=website,
                expires_hours=1
            )
            return Response(
                {"token": token_obj.token, "expires_at": token_obj.expires_at},
                status=status.HTTP_201_CREATED
            )
        except (PermissionDenied, ValueError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=False, methods=["post"])
    def start(self, request):
        """
        Impersonates the target user using a token.
        Returns new JWT tokens for the target user.
        """
        token_str = request.data.get("token")
        if not token_str:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        from websites.utils import get_current_website
        website = get_current_website(request)
        
        service = ImpersonationService(request, website)
        try:
            result = service.impersonate_user(token_str)
            return Response(result, status=status.HTTP_200_OK)
        except (PermissionDenied, ValueError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=False, methods=["post"])
    def end(self, request):
        """
        Ends impersonation and logs back in as original admin user.
        Returns new JWT tokens for the admin.
        """
        from websites.utils import get_current_website
        website = get_current_website(request)
        
        service = ImpersonationService(request, website)
        try:
            result = service.end_impersonation()
            return Response(result, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
    
    @action(detail=False, methods=["get"])
    def status(self, request):
        """
        Get current impersonation status.
        """
        from websites.utils import get_current_website
        website = get_current_website(request)
        
        service = ImpersonationService(request, website)
        is_impersonating = service.is_impersonating()
        impersonator_info = service.get_impersonator_info() if is_impersonating else None
        
        return Response({
            "is_impersonating": is_impersonating,
            "impersonator": impersonator_info
        })

    @action(detail=False, methods=["get"])
    def expired(self, request):
        """
        Lists expired tokens for cleanup or auditing.
        """
        expired_tokens = self.queryset.filter(expires_at__lt=timezone.now())
        serializer = ImpersonationTokenSerializer(expired_tokens, many=True)
        return Response(serializer.data)
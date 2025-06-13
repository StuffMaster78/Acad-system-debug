from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.timezone import now
from rest_framework.permissions import AllowAny
from authentication.models.register import RegistrationToken, RegistrationConfirmationLog
from authentication.serializers import (
    RegistrationTokenSerializer,
    RegistrationTokenValidationSerializer
)
from authentication.services.otp_service import OTPService
from authentication.services.registration_token_service import RegistrationTokenService


class RegistrationTokenViewSet(viewsets.ViewSet):
    """
    Handles registration token validation and user onboarding.
    """

    permission_classes = [AllowAny]

    def create(self, request):
        """
        POST /api/v1/auth/registration/confirm/
        """
        serializer = RegistrationTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user  # or fetch based on token if unauthenticated
        website = request.headers.get("X-Website")  # or however you're passing it
        token = serializer.validated_data['token']
        otp_code = serializer.validated_data['otp_code']

        confirmation_service = RegistrationTokenService(user, website)
        otp_service = OTPService(user, website)

        try:
            confirmation_service.confirm_registration(token, otp_code, otp_service)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Registration confirmed successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"])
    def validate(self, request):
        """
        Validates a registration token and marks it as used if valid.

        Returns:
            200 OK with user info or 400 Bad Request with error message.
        """
        serializer = RegistrationTokenValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = RegistrationTokenService(
            user=request.user,
            website=request.website
        )

        token = serializer.validated_data["token"]

        token_obj = service.validate_token(serializer.validated_data['token'])
        service.mark_used(token_obj)

        try:
            reg_token = RegistrationToken.objects.select_related("user").get(
                token=token,
                is_used=False
            )
        except RegistrationToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or already used token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if reg_token.is_expired():
            return Response(
                {"detail": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reg_token.is_used = True
        reg_token.save()

        # Optionally activate the user here:
        reg_token.user.is_active = True
        reg_token.user.save()

        return Response(
            {
                "detail": "Token valid. Registration complete.",
                "user_id": reg_token.user.id,
                "email": reg_token.user.email
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def validate_otp(self, request):
        otp = request.data.get("otp")
        service = RegistrationTokenService(
            user=request.user,
            website=request.website
        )
        obj = service.validate_otp(otp)
        service.mark_used(obj)
        return Response({"message": "OTP valid. Registration confirmed."})
    
    @action(detail=False, methods=["get"])
    def all(self, request):
        """
        Lists all tokens — for admin/debug only. Lock behind permissions.
        """
        tokens = RegistrationToken.objects.all()
        serializer = RegistrationTokenSerializer(tokens, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def send_email(self, request):
        user = request.user  # or fetch based on request.data
        website = request.website  # assumed multitenant middleware or passed
        service = RegistrationTokenService(user, website)
        token = service.generate_token()
        return Response({"message": "Registration email sent.", "token": str(token.token)})
    
    @action
    def confirm_registration(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        service = RegistrationTokenService(...)
        service.confirm_registration(...)  # implement hybrid logic here

        RegistrationConfirmationLog.objects.create(
            user=user,
            token=registration_token,
            ip_address=ip,
            user_agent=user_agent
        )

        return Response({"detail": "Registration confirmed."})

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.conf import settings
from authentication.utils.jwt import (
    encode_password_reset_token,
    decode_password_reset_token,
)
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from authentication.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetTokenValidationSerializer,
    SetNewPasswordSerializer
)
from authentication.utils.email import send_password_reset_email
from rest_framework.exceptions import ValidationError


User = get_user_model()


class RequestPasswordResetView(APIView):
    """
    Sends a password reset email to the user with a tokenized link.
    """

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Security: don't confirm if email exists
            return Response({"detail": "If that email exists, a reset link was sent."}, status=status.HTTP_200_OK)

        token = encode_password_reset_token(user)

        current_site = get_current_site(request)
        domain = current_site.domain
        path = reverse("password-reset-confirm")
        reset_link = f"https://{domain}{path}?token={token}"

        subject = "Password Reset Request"
        message = (
            f"Hey {user.get_full_name() or user.username},\n\n"
            f"Click the link below to reset your password. The link expires in 30 minutes.\n\n"
            f"{reset_link}\n\n"
            f"If you didn't ask for this, ignore this email."
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return Response({"detail": "If that email exists, a reset link was sent."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    """
    Accepts new password and token, resets the user password.
    """
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not token or not new_password:
            return Response(
                {"detail": "Token and new password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = decode_password_reset_token(token)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)

class SetNewPasswordView(APIView):
    """
    Accepts token + new password and resets user's password.
    """
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        password = serializer.validated_data["password"]
        user.set_password(password)
        user.save()

        return Response(
            {"detail": "Password reset successful."},
            status=status.HTTP_200_OK
        )
    
class ConfirmPasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        password = serializer.validated_data["new_password"]

        user = decode_password_reset_token(token)
        user.set_password(password)
        user.save()

        return Response({"detail": "Password reset successful."})
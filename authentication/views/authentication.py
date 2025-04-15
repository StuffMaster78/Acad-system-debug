from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from authentication.serializers import UserSerializer
from django.core.mail import send_mail
from django.conf import settings
import pyotp  # type: ignore
from authentication.utils_backp import generate_verification_token, generate_totp_secret # Assuming this exists
from rest_framework_simplejwt.views import TokenRefreshView # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from rest_framework_simplejwt.exceptions import InvalidToken # type: ignore
from django.http import JsonResponse
from rest_framework_simplejwt.settings import api_settings # type: ignore


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save(is_active=False)

            enable_mfa = request.data.get("enable_mfa", False)

            if enable_mfa:
                # Generate TOTP secret and store it in the user's profile
                totp_secret = generate_totp_secret()
                user.mfa_secret = totp_secret
                user.save()

                # Generate TOTP provisioning URI (QR code)
                totp = pyotp.TOTP(totp_secret)
                mfa_qr_code = totp.provisioning_uri(name=user.email, issuer_name="MyApp")

                # Send email with verification link and MFA QR code
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{generate_verification_token(user)}"
                send_mail(
                    "Email Verification",
                    f"Click here to verify your email and set up MFA: {verification_url}\n\nScan this QR code with your MFA app: {mfa_qr_code}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

            else:
                # Send verification email without MFA setup
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{generate_verification_token(user)}"
                send_mail(
                    "Email Verification",
                    f"Click here to verify your email: {verification_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

            return Response(
                {"message": "User created. Please check your email to verify your account."},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        
        user = authenticate(email=email, password=password)
        
        if user is not None and user.is_active:
            # If MFA is enabled, ask for the TOTP code
            if user.mfa_secret:
                totp_code = request.data.get("totp_code")
                totp = pyotp.TOTP(user.mfa_secret)

                if not totp.verify(totp_code):
                    return Response(
                        {"error": "Invalid MFA code."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Generate and return access token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response(
                {"access_token": access_token},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "Invalid credentials or account not active."},
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "An error occurred."}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """Handles secure token refresh using cookies."""

    def post(self, request, *args, **kwargs):
        """Refresh token if valid and return a new access token."""
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except InvalidToken:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Create response and set new access token in cookies
        response = JsonResponse({"message": "Token refreshed successfully"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()
        )
        return response
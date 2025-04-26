from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login

from utils.passkey_utils import (
    generate_passkey_registration_options,
    verify_passkey_registration_response,
    generate_passkey_authentication_options,
    verify_passkey_authentication_response,
)
from utils.device_info import parse_device_info

class PasskeyRegistrationVerify(APIView):
    """
    Verify passkey registration and store credential info.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        raw_credential = request.data.get("credential")

        if not token or not raw_credential:
            return Response(
                {"detail": "Missing token or credential."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            device_info = parse_device_info(user_agent)  # 👈 grab + parse it

            user = verify_passkey_registration_response(
                token, 
                raw_credential, 
                device_info=device_info  # 👈 pass it forward
            )

            return Response(
                {"detail": "Passkey registered successfully."},
                status=status.HTTP_201_CREATED
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PasskeyRegistrationVerify(APIView):
    """
    Verify passkey registration and store credential info.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        raw_credential = request.data.get("credential")

        if not token or not raw_credential:
            return Response(
                {"detail": "Missing token or credential."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = verify_passkey_registration_response(token, raw_credential)
            return Response(
                {"detail": "Passkey registered successfully."},
                status=status.HTTP_201_CREATED
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasskeyLoginOptions(APIView):
    """
    Generate passkey login (authentication) options for a user.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response(
                {"detail": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(username=username)

            data = generate_passkey_authentication_options(request, user)
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasskeyLoginVerify(APIView):
    """
    Verify the passkey login and log the user in if successful.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        raw_credential = request.data.get("credential")

        if not token or not raw_credential:
            return Response(
                {"detail": "Missing token or credential."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = verify_passkey_authentication_response(token, raw_credential)
            login(request, user)
            return Response(
                {"detail": "Login successful."},
                status=status.HTTP_200_OK
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
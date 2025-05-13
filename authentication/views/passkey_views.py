from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login

from authentication.utils.passkey_utils import (
    generate_passkey_registration_options,
    verify_passkey_registration_response,
    generate_passkey_authentication_options,
    verify_passkey_authentication_response
)
from authentication.utils.device_info import parse_device_info
import base64
from django.core.cache import cache
from django.contrib.auth import get_user_model
from authentication.models.passkeys import WebAuthnCredential
from fido2.server import Fido2Server
from fido2.webauthn import AuthenticationCredential
from fido2.utils import websafe_decode
from .fido_config import fido_server
from fido2.webauthn import PublicKeyCredentialDescriptor
from fido2.webauthn import AttestationObject, CollectedClientData
from .fido_config import fido_server
from django.core.exceptions import ValidationError
from fido2 import cbor
from django.contrib.auth import get_user_model

User = get_user_model()

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
        
def verify_passkey_authentication_response(token, raw_credential):
    """
    Verify the WebAuthn authentication (passkey login) response
    using the stored challenge and WebAuthn credentials.

    Args:
        token (str): The cache key holding the authentication challenge.
        raw_credential (dict): The JSON credential response from the client.

    Returns:
        User: The authenticated user object.

    Raises:
        Exception: If the authentication fails.
    """
    stored = cache.get(token)
    if not stored:
        raise Exception("Challenge expired or not found.")

    user = User.objects.get(pk=stored["user_id"])

    # Fetch registered credentials for the user
    creds = WebAuthnCredential.objects.filter(user=user)
    credentials = [cred.to_credential_descriptor() for cred in creds]

    auth_data = AuthenticationCredential.parse(raw_credential)
    auth_result = fido_server.authenticate_complete(
        state=stored["state"],
        credentials=credentials,
        credential_id=websafe_decode(raw_credential["id"]),
        client_data=auth_data.client_data,
        auth_data=auth_data.auth_data,
        signature=auth_data.signature,
    )

    # Update sign count in DB
    cred = WebAuthnCredential.objects.get(
        user=user,
        credential_id=base64.urlsafe_b64decode(raw_credential["id"] + "==")
    )
    cred.sign_count = auth_result.new_sign_count
    cred.save()

    return user



def to_credential_descriptor(self):
    """
    Converts the stored credential to a PublicKeyCredentialDescriptor
    required for FIDO2 authentication.

    Returns:
        PublicKeyCredentialDescriptor: Credential descriptor instance.
    """
    return PublicKeyCredentialDescriptor(
        id=base64.urlsafe_b64decode(self.credential_id + "==")
    )
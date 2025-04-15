from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.http import Http404

from authentication.models.passkeys import WebAuthnCredential
from websites.models import Website 

from webauthn import (  # type: ignore
    generate_registration_options,
    options_to_json,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)

from webauthn.helpers.structs import (  # type: ignore
    RegistrationCredential,
    AuthenticationCredential,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
)

User = get_user_model()


def get_rp_info(request):
    """Extract Relying Party (RP) domain and ID from Website model."""
    # Get the host domain, excluding port
    host = request.get_host().split(":")[0]  
    # Fetch the website object from the database
    site = get_object_or_404(Website, domain=host)
    return {
        "id": site.domain,  # Relying Party ID (usually the domain)
        "name": site.name,  # Relying Party Name
    }


class PasskeyRegistrationOptions(APIView):
    """
    Returns WebAuthn registration options for the logged-in user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get RP details based on the current host
        rp = get_rp_info(request)
        # Get the logged-in user  
        user = request.user 

        # Generate WebAuthn registration options for the user
        registration_options = generate_registration_options(
            rp_id=rp["id"],  # RP ID
            rp_name=rp["name"],  # RP name
            user_id=str(user.id).encode(),  # User ID (as a byte string)
            user_name=user.username,  # Username for identification
            user_display_name=user.get_full_name() or user.username,  # Full name or username for display
            authenticator_selection={"user_verification": "preferred"},  # User verification preference
        )

        # Store the challenge in the session for later verification
        request.session["passkey_challenge"] = registration_options.challenge.decode()

        return Response(options_to_json(registration_options))  # Send registration options as JSON


class PasskeyRegistrationVerify(APIView):
    """
    Verifies a WebAuthn registration credential and stores it.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        challenge = request.session.get("passkey_challenge")
        if not challenge:
            return Response({"detail": "No challenge in session."}, status=400)

        rp = get_rp_info(request)
        user = request.user

        try:
            # Parse the registration credential from the request body
            credential = RegistrationCredential.parse_raw(request.body)

            # Verify the registration response
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=challenge,
                expected_rp_id=rp["id"],
                expected_origin=f"https://{rp['id']}",
                require_user_verification=True,
            )

            # Save the WebAuthn credential to the database
            WebAuthnCredential.objects.create(
                user=user,
                credential_id=verification.credential_id.decode(),
                public_key=verification.credential_public_key.decode(),
                sign_count=verification.sign_count,
                transports=credential.transports or [],
            )

            return Response({"detail": "Passkey registered."}, status=201)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class PasskeyLoginOptions(APIView):
    """
    Returns authentication options for WebAuthn login.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            username = request.data.get("username")
            # Fetch user by username
            user = get_object_or_404(User, username=username) 
            creds = WebAuthnCredential.objects.filter(user=user)

            if not creds.exists():
                raise Http404("No passkeys for this user.")

            rp = get_rp_info(request)

            # Prepare list of credentials that the user can authenticate with
            allow_credentials = [
                PublicKeyCredentialDescriptor(id=bytes.fromhex(cred.credential_id))
                for cred in creds
            ]

            # Generate WebAuthn authentication options
            auth_options = generate_authentication_options(
                rp_id=rp["id"],
                allow_credentials=allow_credentials,
                user_verification=UserVerificationRequirement.PREFERRED,
            )

            # Store challenge and user information in session for verification
            request.session["passkey_challenge"] = auth_options.challenge.decode()
            request.session["passkey_user"] = user.pk

            return Response(options_to_json(auth_options))

        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class PasskeyLoginVerify(APIView):
    """
    Verifies the authentication response and logs in the user.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        challenge = request.session.get("passkey_challenge")
        user_id = request.session.get("passkey_user")

        if not challenge or not user_id:
            return Response({"detail": "Missing session challenge or user."}, status=400)

        user = get_object_or_404(User, pk=user_id)
        rp = get_rp_info(request)

        try:
            # Parse the authentication credential from the request body
            credential = AuthenticationCredential.parse_raw(request.body)
            cred = get_object_or_404(WebAuthnCredential, user=user, credential_id=credential.raw_id.decode())

            # Verify the authentication response
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=challenge,
                expected_rp_id=rp["id"],
                expected_origin=f"https://{rp['id']}",
                credential_public_key=cred.public_key.encode(),
                credential_current_sign_count=cred.sign_count,
                require_user_verification=True,
            )

            # Update the sign count after successful authentication
            cred.sign_count = verification.new_sign_count
            cred.save()

            # Log the user in (this could be session-based, token-based, etc.)
            from django.contrib.auth import login
            login(request, user)

            return Response({"detail": "Passkey login successful."})

        except Exception as e:
            return Response({"detail": str(e)}, status=400)
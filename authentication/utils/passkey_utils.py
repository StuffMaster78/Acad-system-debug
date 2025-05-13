# utils/passkey_utils.py

import uuid
import json

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json
)
from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticationCredential,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor
)
from django.conf import settings
from authentication.models.passkeys import WebAuthnCredential
from websites.models import Website
from authentication.utils.device_info import (
    generate_device_fingerprint,
    generate_device_label
)

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


User = get_user_model()

def get_rp_info(request):
    """
    Retrieve relying party (RP) ID and name based on request domain.
    """
    host = request.get_host().split(":")[0]
    site = get_object_or_404(Website, domain=host)

    return {
        "id": site.domain,
        "name": site.name,
    }

def build_redis_key(domain, token):
    """
    Build a namespaced Redis key for passkey operations.
    """
    return f"{settings.PASSKEY_REDIS_PREFIX}:{domain}:{token}"


def cache_challenge(token, challenge, domain, user_id=None, ttl=None):
    """
    Store challenge and user_id in Redis under a domain-scoped key.
    """
    key = build_redis_key(domain, token)
    payload = {"challenge": challenge, "user_id": user_id}
    cache.set(key, json.dumps(payload), timeout=ttl or settings.PASSKEY_CHALLENGE_TTL)


def get_cached_challenge(token, domain, delete=True):
    """
    Retrieve and delete challenge from Redis using domain and token.
    """
    key = build_redis_key(domain, token)
    payload = cache.get(key)
    if not payload:
        raise Http404("Challenge not found or expired.")

    if delete:
        cache.delete(key)

    return json.loads(payload)

def delete_challenge(token):
    """
    Manually delete a cached passkey challenge.
    """
    key = f"{settings.PASSKEY_REDIS_PREFIX}{token}"
    cache.delete(key)

def generate_passkey_registration_options(request, user):
    """
    Generate WebAuthn registration options and store challenge in Redis.
    """
    rp = get_rp_info(request)

    options = generate_registration_options(
        rp_id=rp["id"],
        rp_name=rp["name"],
        user_id=str(user.id).encode(),
        user_name=user.username,
        user_display_name=user.get_full_name() or user.username,
        authenticator_selection={"user_verification": "preferred"},
    )

    token = str(uuid.uuid4())
    cache_challenge(
        domain=rp["id"],
        token=token,
        challenge=options.challenge.decode(),
        user_id=user.id,
    )

    return {"options": options_to_json(options), "token": token}


def verify_passkey_registration_response(request, token, response_data):
    """
    Verify registration response using cached challenge and store credentials.
    """
    rp = get_rp_info(request)
    challenge_info = get_cached_challenge(rp["id"], token)

    user = get_object_or_404(User, pk=challenge_info["user_id"])

    try:
        credential = RegistrationCredential.parse_raw(response_data)

        verification = verify_registration_response(
            credential=credential,
            expected_challenge=challenge_info["challenge"],
            expected_rp_id=rp["id"],
            expected_origin=f"https://{rp['id']}",
            require_user_verification=True,
        )

        WebAuthnCredential.objects.create(
            user=user,
            credential_id=verification.credential_id.decode(),
            public_key=verification.credential_public_key.decode(),
            sign_count=verification.sign_count,
            transports=credential.transports or [],
        )

        return user
    except Exception as exc:
        raise Http404(f"Registration verification failed: {exc}")


def generate_passkey_authentication_options(request, user):
    """
    Generate WebAuthn authentication options and store challenge in Redis.
    """
    rp = get_rp_info(request)
    credentials = WebAuthnCredential.objects.filter(user=user)

    if not credentials.exists():
        raise Http404("No passkeys registered for this user.")

    allow_credentials = [
        PublicKeyCredentialDescriptor(id=cred.credential_id.encode())
        for cred in credentials
    ]

    options = generate_authentication_options(
        rp_id=rp["id"],
        allow_credentials=allow_credentials,
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    token = str(uuid.uuid4())
    cache_challenge(
        domain=rp["id"],
        token=token,
        challenge=options.challenge.decode(),
        user_id=user.id,
    )

    return {"options": options_to_json(options), "token": token}


def verify_passkey_registration_response(token, response_data, device_info=None):
    """
    Verify registration response using cached challenge and store credentials.
    """
    data = get_cached_challenge(token)
    user = get_object_or_404(User, pk=data["user_id"])
    rp = get_rp_info()

    try:
        credential = RegistrationCredential.parse_raw(response_data)
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=data["challenge"],
            expected_rp_id=rp["id"],
            expected_origin=f"https://{rp['id']}",
            require_user_verification=True,
        )

        device_fp = None
        device_label = None
        if device_info:
            device_fp = generate_device_fingerprint(device_info)
            device_label = generate_device_label(device_info)

        WebAuthnCredential.objects.create(
            user=user,
            credential_id=verification.credential_id.decode(),
            public_key=verification.credential_public_key.decode(),
            sign_count=verification.sign_count,
            transports=credential.transports or [],
            device_info=device_info or {},
            device_fingerprint=device_fp,  # 👈 Save fingerprint
            device_label=device_label, 
        )

        return user
    except Exception as exc:
        raise Http404(f"Registration failed: {exc}")
    


def verify_passkey_registration_response(token, client_data_json, attestation_object):
    """
    Finalizes passkey registration by verifying attestation data
    and saving the credential.

    Args:
        token (str): Cache token used to retrieve the challenge/state.
        client_data_json (bytes): Client data in JSON format.
        attestation_object (bytes): Attestation object returned by the client.

    Returns:
        WebAuthnCredential: Saved credential instance.

    Raises:
        Exception: If registration fails or challenge expired.
    """
    stored = cache.get(token)
    if not stored:
        raise Exception("Challenge expired or not found.")

    client_data = CollectedClientData(client_data_json)
    att_obj = AttestationObject(attestation_object)

    auth_data = fido_server.register_complete(
        state=stored["state"],
        client_data=client_data,
        attestation_object=att_obj
    )

    credential = WebAuthnCredential.objects.create(
        user_id=stored["user_id"],
        credential_id=auth_data.credential_id,
        public_key=auth_data.credential_public_key,
        sign_count=auth_data.sign_count
    )

    return credential


def verify_passkey_authentication_response(token, raw_credential):
    """
    Verifies the WebAuthn authentication response from the client (passkey).
    If the response is valid, it returns the user associated with the credential.

    :param token: The challenge token used in the authentication request.
    :param raw_credential: The credential data returned from the client, containing
                            the signed assertion and other necessary info.
    :return: user: The user associated with the valid passkey.
    :raises ValidationError: If any part of the authentication is invalid.
    """
    try:
        # Decode and parse the response (token + credential data)
        raw_response = cbor.loads(raw_credential)
        credential_data = raw_response['credential']
        signature = raw_response['signature']
        client_data_json = raw_response['clientDataJSON']
        authenticator_data = raw_response['authenticatorData']
        
        # Retrieve the WebAuthn credential object from the database
        credential = WebAuthnCredential.objects.get(credential_id=credential_data['id'])
        
        # Get the stored public key for the credential
        public_key = base64.urlsafe_b64decode(credential.public_key)
        
        # Create a Fido2Server instance with the RP (relying party) details
        rp = {
            "id": "example.com",  # Replace with actual RP ID from your config
            "name": "Example",
        }
        
        server = Fido2Server(rp)
        
        # Verify the signature and other parts of the authentication response
        try:
            user = server.authenticate_assertion(
                credential, authenticator_data, client_data_json, signature
            )
        except Exception as e:
            raise ValidationError(f"Authentication failed: {str(e)}")
        
        # If authentication is successful, return the user
        return credential.user

    except WebAuthnCredential.DoesNotExist:
        raise ValidationError("Credential not found.")
    except Exception as e:
        raise ValidationError(f"Authentication error: {str(e)}")
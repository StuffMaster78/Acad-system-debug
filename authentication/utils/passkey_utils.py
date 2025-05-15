import uuid
import json
import base64

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings

from fido2.webauthn import ( # type: ignore
    PublicKeyCredentialDescriptor,
    AttestationObject,
    CollectedClientData,
)
from fido2 import cbor  # type: ignore

from utils.fido_config import get_fido_server
from authentication.models.passkeys import WebAuthnCredential
from authentication.utils.device_info import (
    generate_device_fingerprint,
    generate_device_label,
)
from websites.models import Website

User = get_user_model()


def get_rp_info(request):
    """
    Extract RP (Relying Party) ID and name based on request host.

    Args:
        request (HttpRequest): Incoming HTTP request.

    Returns:
        dict: RP info with 'id' and 'name'.
    """
    host = request.get_host().split(":")[0]
    site = get_object_or_404(Website, domain=host)
    return {"id": site.domain, "name": site.name}


def build_redis_key(domain, token):
    """
    Constructs a Redis key for storing passkey challenge state.

    Args:
        domain (str): Domain of the tenant site.
        token (str): UUID token.

    Returns:
        str: Fully constructed Redis key.
    """
    return f"{settings.PASSKEY_REDIS_PREFIX}:{domain}:{token}"


def cache_challenge(token, challenge, domain, user_id=None, ttl=None):
    """
    Caches a WebAuthn challenge to Redis.

    Args:
        token (str): UUID token.
        challenge (str): The FIDO2 challenge string.
        domain (str): Domain of the tenant.
        user_id (int, optional): Associated user ID.
        ttl (int, optional): Expiry time in seconds.
    """
    key = build_redis_key(domain, token)
    payload = {"challenge": challenge, "user_id": user_id}
    cache.set(key, json.dumps(payload), timeout=ttl or
              settings.PASSKEY_CHALLENGE_TTL)


def get_cached_challenge(token, domain, delete=True):
    """
    Retrieves a cached WebAuthn challenge.

    Args:
        token (str): Challenge token.
        domain (str): Domain of the tenant.
        delete (bool): Whether to delete after retrieval.

    Returns:
        dict: Challenge payload.

    Raises:
        Http404: If challenge is missing or expired.
    """
    key = build_redis_key(domain, token)
    payload = cache.get(key)
    if not payload:
        raise Http404("Challenge not found or expired.")
    if delete:
        cache.delete(key)
    return json.loads(payload)


def delete_challenge(token, domain):
    """
    Deletes a challenge from Redis.

    Args:
        token (str): Challenge token.
        domain (str): Tenant domain.
    """
    key = build_redis_key(domain, token)
    cache.delete(key)


def generate_passkey_registration_options(request, user):
    """
    Begins the registration ceremony and returns challenge options.

    Args:
        request (HttpRequest): Incoming request.
        user (User): Django User object.

    Returns:
        dict: Registration options and token.
    """
    fido_server = get_fido_server(request)
    rp = get_rp_info(request)

    user_id = str(user.id).encode()
    user_name = user.username
    user_display_name = user.get_full_name() or user.username

    registration_data, state = fido_server.register_begin(
        {
            "id": user_id,
            "name": user_name,
            "displayName": user_display_name,
        },
        user_verification="preferred"
    )

    token = str(uuid.uuid4())
    cache.set(
        token,
        {"state": state, "user_id": user.id},
        timeout=settings.PASSKEY_CHALLENGE_TTL
    )

    return {"options": registration_data, "token": token}


def verify_passkey_registration_response(
    request,
    token,
    client_data_json,
    attestation_object,
    device_info=None
):
    """
    Verifies the registration response and stores credential.

    Args:
        request (HttpRequest): Request object.
        token (str): Registration token.
        client_data_json (bytes): Collected client data.
        attestation_object (bytes): Attestation object.
        device_info (dict, optional): Parsed client device metadata.

    Returns:
        WebAuthnCredential: Created credential instance.

    Raises:
        ValidationError: If registration fails.
        Http404: If challenge is missing or expired.
    """
    fido_server = get_fido_server(request)
    stored = cache.get(token)
    if not stored:
        raise Http404("Challenge expired or not found.")

    client_data = CollectedClientData(client_data_json)
    att_obj = AttestationObject(attestation_object)

    try:
        auth_data = fido_server.register_complete(
            stored["state"],
            client_data,
            att_obj
        )
    except Exception as e:
        raise ValidationError(f"Registration failed: {str(e)}")

    user = get_object_or_404(User, pk=stored["user_id"])

    device_fp = (generate_device_fingerprint(device_info)
                 if device_info else None)
    device_label = (generate_device_label(device_info)
                    if device_info else None)

    credential = WebAuthnCredential.objects.create(
        user=user,
        credential_id=auth_data.credential_id.decode(),
        public_key=auth_data.credential_public_key.decode(),
        sign_count=auth_data.sign_count,
        device_info=device_info or {},
        device_fingerprint=device_fp,
        device_label=device_label,
    )

    return credential


def generate_passkey_authentication_options(request, user):
    """
    Begins the authentication ceremony and returns challenge options.

    Args:
        request (HttpRequest): HTTP request object.
        user (User): Django User instance.

    Returns:
        dict: Authentication options and token.

    Raises:
        Http404: If no credentials are found.
    """
    fido_server = get_fido_server(request)
    rp = get_rp_info(request)

    credentials = WebAuthnCredential.objects.filter(user=user)
    if not credentials.exists():
        raise Http404("No passkeys registered for this user.")

    allowed_credentials = [
        PublicKeyCredentialDescriptor(
            id=base64.urlsafe_b64decode(c.credential_id.encode())
        )
        for c in credentials
    ]

    auth_data, state = fido_server.authenticate_begin(
        allowed_credentials,
        user_verification="preferred"
    )
    token = str(uuid.uuid4())

    cache.set(
        token,
        {"state": state, "user_id": user.id},
        timeout=settings.PASSKEY_CHALLENGE_TTL
    )

    return {"options": auth_data, "token": token}


def verify_passkey_authentication_response(
    request,
    token,
    credential_data,
    client_data_json,
    authenticator_data,
    signature
):
    """
    Verifies the authentication response and returns the authenticated user.

    Args:
        request (HttpRequest): HTTP request.
        token (str): Authentication token.
        credential_data (dict): Credential JSON.
        client_data_json (bytes): Client data.
        authenticator_data (bytes): Authenticator output.
        signature (bytes): Signed challenge.

    Returns:
        User: Authenticated Django User instance.

    Raises:
        ValidationError: If signature fails verification.
        Http404: If challenge or credential is missing.
    """
    fido_server = get_fido_server(request)
    stored = cache.get(token)
    if not stored:
        raise Http404("Authentication challenge expired or not found.")

    credential = get_object_or_404(
        WebAuthnCredential,
        credential_id=credential_data["id"]
    )

    try:
        fido_server.authenticate_complete(
            state=stored["state"],
            credential_id=credential_data["id"],
            client_data=CollectedClientData(client_data_json),
            auth_data=authenticator_data,
            signature=signature,
            credential_public_key=base64.urlsafe_b64decode(
                credential.public_key
            )
        )
        return credential.user
    except Exception as e:
        raise ValidationError(f"Authentication failed: {str(e)}")
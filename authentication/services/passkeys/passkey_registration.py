import uuid
import json

from django.core.cache import cache
from django.http import Http404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from fido2.server import Fido2Server # type: ignore
from fido2.webauthn import ( # type: ignore
    AttestationObject,
    CollectedClientData,
    PublicKeyCredentialDescriptor,
)
from fido2.utils import websafe_decode # type: ignore

from authentication.models.passkeys import WebAuthnCredential
from authentication.utils.device_info import (
    generate_device_fingerprint,
    generate_device_label
)
from utils.fido_config import fido_server
from utils.fido_rp import get_rp_info

from django.conf import settings

User = get_user_model()


def build_redis_key(domain: str, token: str) -> str:
    return f"{settings.PASSKEY_REDIS_PREFIX}:{domain}:{token}"


def cache_challenge(domain, token, state, user_id, ttl=None):
    payload = {"state": state, "user_id": user_id}
    key = build_redis_key(domain, token)
    cache.set(key, json.dumps(payload), timeout=ttl or settings.PASSKEY_CHALLENGE_TTL)


def get_cached_challenge(domain, token, delete=True):
    key = build_redis_key(domain, token)
    payload = cache.get(key)
    if not payload:
        raise Http404("Challenge expired or not found.")
    if delete:
        cache.delete(key)
    return json.loads(payload)


def generate_registration_options(request, user):
    """
    Generate FIDO2 registration options and cache the challenge state.
    """
    rp = get_rp_info(request)

    options, state = fido_server.register_begin(
        user={
            "id": str(user.id).encode(),
            "name": user.username,
            "displayName": user.get_full_name() or user.username,
        },
        user_verification="preferred",
        rp_id=rp["id"],
    )

    token = str(uuid.uuid4())
    cache_challenge(rp["id"], token, state, user.id)

    return {"options": options, "token": token}


def verify_registration_response(request, token, client_data_json, attestation_object, device_info=None):
    """
    Complete registration and store credential in DB.
    """
    rp = get_rp_info(request)
    data = get_cached_challenge(rp["id"], token)

    try:
        client_data = CollectedClientData(client_data_json)
        att_obj = AttestationObject(attestation_object)

        auth_data = fido_server.register_complete(
            state=data["state"],
            client_data=client_data,
            attestation_object=att_obj
        )

        user = User.objects.get(pk=data["user_id"])

        WebAuthnCredential.objects.create(
            user=user,
            credential_id=auth_data.credential_id,
            public_key=auth_data.credential_public_key,
            sign_count=auth_data.sign_count,
            device_info=device_info or {},
            device_fingerprint=generate_device_fingerprint(device_info) if device_info else None,
            device_label=generate_device_label(device_info) if device_info else None,
        )

        return user
    except Exception as exc:
        raise ValidationError(f"Registration failed: {str(exc)}")
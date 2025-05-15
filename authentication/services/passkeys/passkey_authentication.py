import json
import base64
import uuid

from django.core.cache import cache
from django.http import Http404
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from fido2.server import Fido2Server # type: ignore
from fido2 import cbor # type: ignore
from fido2.webauthn import ( # type: ignore
    PublicKeyCredentialDescriptor,
    CollectedClientData,
    AuthenticatorData
)

from authentication.models.passkeys import WebAuthnCredential
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


def generate_authentication_options(request, user):
    """
    Generate options for WebAuthn authentication and store state in Redis.
    """
    rp = get_rp_info(request)

    credentials = WebAuthnCredential.objects.filter(user=user)
    if not credentials.exists():
        raise Http404("No credentials registered for this user.")

    allow_credentials = [
        PublicKeyCredentialDescriptor(id=cred.credential_id)
        for cred in credentials
    ]

    options, state = fido_server.authenticate_begin(
        credentials=allow_credentials,
        user_verification="preferred"
    )

    token = str(uuid.uuid4())
    cache_challenge(rp["id"], token, state, user.id)

    return {"options": options, "token": token}


def verify_authentication_response(request, token, raw_response):
    """
    Verify WebAuthn passkey authentication response and return the user.
    """
    rp = get_rp_info(request)
    challenge_data = get_cached_challenge(rp["id"], token)

    try:
        parsed = cbor.loads(raw_response)

        credential_id = parsed["credentialId"]
        client_data = CollectedClientData(parsed["clientDataJSON"])
        auth_data = AuthenticatorData(parsed["authenticatorData"])
        signature = parsed["signature"]

        credential = WebAuthnCredential.objects.get(credential_id=credential_id)

        fido_server.authenticate_complete(
            state=challenge_data["state"],
            credential_id=credential.credential_id,
            client_data=client_data,
            authenticator_data=auth_data,
            signature=signature,
            credential_public_key=credential.public_key,
            sign_count=credential.sign_count
        )

        return credential.user

    except WebAuthnCredential.DoesNotExist:
        raise ValidationError("Credential not found.")
    except Exception as exc:
        raise ValidationError(f"Authentication failed: {str(exc)}")
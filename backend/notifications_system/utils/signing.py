from __future__ import annotations

import hmac
import hashlib
from typing import Optional


def hmac_sign(payload: bytes, secret: str, algo: str = "sha256") -> str:
    """Return hex HMAC digest for a payload.

    Args:
        payload: Raw bytes to sign.
        secret: Shared secret string.
        algo: Hash algorithm: 'sha1' or 'sha256'.

    Returns:
        Hex digest string.
    """
    alg = hashlib.sha1 if algo == "sha1" else hashlib.sha256
    return hmac.new(secret.encode(), payload, alg).hexdigest()


def hmac_verify(payload: bytes, secret: str, sent: str,
                algo: str = "sha256") -> bool:
    """Constant-time compare of computed HMAC vs provided value."""
    expected = hmac_sign(payload, secret, algo=algo)
    return hmac.compare_digest(expected, sent or "")
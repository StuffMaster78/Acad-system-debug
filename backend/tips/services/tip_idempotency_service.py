from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction

from tips.models.tip_idempotency import TipIdempotencyKey


class TipIdempotencyError(Exception):
    """
    Raised when idempotency rules are violated.
    """
    pass


class TipIdempotencyService:
    """
    Ensures safe, retry-proof tip creation.

    Guarantees:
    - Same sender + key cannot create duplicate tips
    - Same key must always represent same payload
    - Safe for concurrent requests
    """

    # -------------------------------------------------------------- #
    # HASHING
    # -------------------------------------------------------------- #

    @staticmethod
    def generate_hash(payload: dict[str, Any]) -> str:
        """
        Canonical JSON hashing for stable idempotency checks.
        """
        normalized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(normalized).hexdigest()

    # -------------------------------------------------------------- #
    # CORE GUARD
    # -------------------------------------------------------------- #

    @classmethod
    @transaction.atomic
    def get_or_create_key(
        cls,
        *,
        sender,
        key: str,
        payload: dict[str, Any],
    ):
        """
        Retrieves or creates an idempotency record safely.
        """

        request_hash = cls.generate_hash(payload)

        obj, created = TipIdempotencyKey.objects.select_for_update().get_or_create(
            sender=sender,
            key=key,
            defaults={
                "request_hash": request_hash,
            },
        )

        # ---------------------------------------------------------- #
        # EXISTING RECORD VALIDATION
        # ---------------------------------------------------------- #

        if not created:
            if obj.request_hash != request_hash:
                raise TipIdempotencyError(
                    "Idempotency key reused with different payload."
                )

        return obj, created

    # -------------------------------------------------------------- #
    # BIND TIP AFTER CREATION
    # -------------------------------------------------------------- #

    @staticmethod
    def bind_tip(
        *,
        idempotency_obj: TipIdempotencyKey,
        tip,
    ) -> None:
        """
        Links created tip to idempotency record.
        """
        idempotency_obj.tip = tip
        idempotency_obj.save(update_fields=["tip"])
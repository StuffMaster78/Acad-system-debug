from __future__ import annotations

from django.db import transaction

from writer_compensation.models.idempotency_models import IdempotencyRecord


class IdempotencyService:
    """
    HARD guarantee: same request cannot execute twice.
    """

    @staticmethod
    def execute(key: str, scope: str, fn):
        if not key:
            return fn()

        with transaction.atomic():
            existing = IdempotencyRecord.objects.filter(
                key=key,
                scope=scope,
            ).first()

            if existing:
                return existing.response

            result = fn()

            IdempotencyRecord.objects.create(
                key=key,
                scope=scope,
                response=result,
            )

            return result
from __future__ import annotations

from django.db import transaction

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


class TipFailureService:
    """
    Force-mark a tip as failed (admin ops tool).
    """

    @classmethod
    @transaction.atomic
    def fail(cls, *, tip: Tip, triggered_by):

        if tip.status == TipStatus.SUCCEEDED:
            return tip

        tip.status = TipStatus.FAILED
        tip.save(update_fields=["status"])

        return tip
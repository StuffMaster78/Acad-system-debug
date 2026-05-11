from __future__ import annotations

from django.db import transaction

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


class TipRetryService:
    """
    Retries a failed or stuck tip.
    """

    @classmethod
    @transaction.atomic
    def retry(cls, *, tip: Tip, triggered_by):

        if tip.status not in {
            TipStatus.FAILED,
            TipStatus.PROCESSING,
        }:
            return tip

        tip.status = TipStatus.PENDING
        tip.save(update_fields=["status"])

        return tip
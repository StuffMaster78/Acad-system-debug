from __future__ import annotations

from django.db import transaction

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


class TipCancelService:
    """
    Cancels a pending tip.
    """

    @classmethod
    @transaction.atomic
    def cancel(cls, *, tip: Tip, triggered_by):

        if tip.status != TipStatus.PENDING:
            return tip

        tip.status = TipStatus.CANCELLED
        tip.save(update_fields=["status"])

        return tip
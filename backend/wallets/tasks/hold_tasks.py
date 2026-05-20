from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from wallets.constants import WalletHoldStatus
from wallets.models import WalletHold
from wallets.services import WalletHoldService


logger = logging.getLogger(__name__)


@shared_task(name="wallets.tasks.expire_active_holds")
def expire_active_holds() -> int:
    """
    Expire wallet holds whose expiry timestamp has passed.
    """
    now = timezone.now()
    holds = WalletHold.objects.filter(
        status=WalletHoldStatus.ACTIVE,
        expires_at__isnull=False,
        expires_at__lte=now,
    )

    expired_count = 0
    for hold in holds.iterator():
        try:
            WalletHoldService.expire_hold(hold=hold)
            expired_count += 1
        except Exception:
            logger.exception("Failed to expire wallet hold %s", hold.pk)

    return expired_count

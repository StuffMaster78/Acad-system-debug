from __future__ import annotations

import logging

from celery import shared_task

from wallets.models import Wallet
from wallets.services import WalletReconciliationService


logger = logging.getLogger(__name__)


@shared_task(name="wallets.tasks.reconcile_all_wallets")
def reconcile_all_wallets() -> dict[str, int]:
    """
    Scan canonical wallets for cached-balance drift.

    The task reports drift; it does not mutate balances. Repairs remain an
    explicit admin action so finance can review inconsistencies.
    """
    checked = 0
    drifted = 0

    for wallet in Wallet.objects.select_related("website").iterator():
        checked += 1
        try:
            if WalletReconciliationService.wallet_has_drift(wallet=wallet):
                drifted += 1
                logger.warning("Wallet %s has reconciliation drift", wallet.pk)
        except Exception:
            logger.exception("Failed to reconcile wallet %s", wallet.pk)

    return {
        "checked": checked,
        "drifted": drifted,
    }

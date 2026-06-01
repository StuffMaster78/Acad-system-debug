"""
Quota recalculation tasks.
Runs nightly to fix drift and alert on near-quota tenants.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def recalculate_all_quotas():
    """
    Recalculate storage quotas for all tenants.

    Fixes drift from failed uploads, manual storage deletions,
    or interrupted cleanup tasks. Run nightly via Celery beat.
    """
    from files_management.services.quota_service import QuotaService

    results = QuotaService.recalculate_all_quotas()

    total_drift = sum(r.get("drift_size", 0) for r in results)
    if total_drift > 0:
        logger.info(
            "Quota recalculation complete: %d tenants, total drift: %d bytes",
            len(results),
            total_drift,
        )
    else:
        logger.info(
            "Quota recalculation complete: %d tenants, no drift",
            len(results),
        )

    # Check for near-quota tenants
    near_quota = QuotaService.get_near_quota_tenants()
    for tenant in near_quota:
        logger.warning(
            "Tenant '%s' approaching quota: %.1f%% used (%d bytes remaining)",
            tenant["website"],
            tenant["usage_percent"],
            tenant["remaining_bytes"],
        )

    return {
        "tenants_checked": len(results),
        "total_drift_bytes": total_drift,
        "near_quota_count": len(near_quota),
    }

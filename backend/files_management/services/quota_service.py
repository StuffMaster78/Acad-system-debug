"""
Quota Service
===============

Manages per-tenant storage quotas. Called during upload validation
and by the nightly recalculation task.

Configuration per tenant is stored in ``FileQuota`` model.
Defaults are generous (10 GB total, 100 MB per file) and can be
adjusted per tenant in the admin.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db.models import Sum, Count

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class QuotaService:
    """Per-tenant storage quota management."""

    @classmethod
    def check_upload_allowed(
        cls,
        website,
        file_size_bytes: int,
    ) -> dict:
        """
        Check whether an upload of ``file_size_bytes`` is allowed
        for this tenant.

        Returns:
            {
                "allowed": True/False,
                "reason": "..." if not allowed,
                "usage_percent": float,
                "remaining_bytes": int,
            }
        """
        from files_management.models.file_quota import FileQuota

        quota, _ = FileQuota.objects.get_or_create(website=website)

        # Check per-file limit
        if file_size_bytes > quota.max_file_size_bytes:
            return {
                "allowed": False,
                "reason": (
                    f"File size ({file_size_bytes:,} bytes) exceeds "
                    f"maximum ({quota.max_file_size_bytes:,} bytes)"
                ),
                "usage_percent": quota.usage_percent,
                "remaining_bytes": quota.remaining_bytes,
            }

        # Check total quota
        projected = quota.current_size_bytes + file_size_bytes
        if projected > quota.max_total_size_bytes:
            return {
                "allowed": False,
                "reason": (
                    f"Upload would exceed tenant quota "
                    f"({quota.usage_percent:.1f}% used, "
                    f"{quota.remaining_bytes:,} bytes remaining)"
                ),
                "usage_percent": quota.usage_percent,
                "remaining_bytes": quota.remaining_bytes,
            }

        # Check file count
        if quota.current_files_count >= quota.max_files_count:
            return {
                "allowed": False,
                "reason": (
                    f"Maximum file count reached ({quota.max_files_count:,})"
                ),
                "usage_percent": quota.usage_percent,
                "remaining_bytes": quota.remaining_bytes,
            }

        return {
            "allowed": True,
            "reason": None,
            "usage_percent": quota.usage_percent,
            "remaining_bytes": quota.remaining_bytes,
        }

    @classmethod
    def recalculate_quota(cls, website) -> dict:
        """
        Recalculate the actual usage for a tenant by counting
        live files in the database. Fixes any drift from failed
        uploads, manual deletions, etc.

        Returns the updated counts.
        """
        from files_management.enums import FileLifecycleStatus
        from files_management.models.file_quota import FileQuota
        from files_management.models.managed_file import ManagedFile

        # Count only active, non-derivative files
        live_files = ManagedFile.objects.filter(
            website=website,
            lifecycle_status=FileLifecycleStatus.ACTIVE,
            parent_file__isnull=True, # exclude derivatives
        )

        aggregates = live_files.aggregate(
            total_size=Sum("file_size_bytes"),
            total_count=Count("id"),
        )

        total_size = aggregates["total_size"] or 0
        total_count = aggregates["total_count"] or 0

        # Also count derivatives (they use quota too)
        derivative_size = ManagedFile.objects.filter(
            website=website,
            lifecycle_status=FileLifecycleStatus.ACTIVE,
            parent_file__isnull=False,
        ).aggregate(total=Sum("file_size_bytes"))["total"] or 0

        combined_size = total_size + derivative_size

        quota, _ = FileQuota.objects.get_or_create(website=website)
        old_size = quota.current_size_bytes
        old_count = quota.current_files_count

        quota.current_size_bytes = combined_size
        quota.current_files_count = total_count
        quota.save(update_fields=["current_size_bytes", "current_files_count"])

        drift_size = abs(combined_size - old_size)
        drift_count = abs(total_count - old_count)

        if drift_size > 0 or drift_count > 0:
            logger.info(
                "Quota recalculated for '%s': "
                "size %d → %d (drift: %d), "
                "count %d → %d (drift: %d)",
                website,
                old_size,
                combined_size,
                drift_size,
                old_count,
                total_count,
                drift_count,
            )

        return {
            "website": str(website),
            "total_size_bytes": combined_size,
            "total_files": total_count,
            "derivative_size_bytes": derivative_size,
            "usage_percent": quota.usage_percent,
            "drift_size": drift_size,
            "drift_count": drift_count,
        }

    @classmethod
    def recalculate_all_quotas(cls) -> list[dict]:
        """Recalculate quotas for all tenants. Called by nightly task."""
        from django.apps import apps

        try:
            Website = apps.get_model("websites", "Website")
            results = []
            for website in Website.objects.filter(is_active=True):
                result = cls.recalculate_quota(website)
                results.append(result)
            return results
        except Exception as exc:
            logger.error("Quota recalculation failed: %s", exc)
            return []

    @classmethod
    def get_near_quota_tenants(cls, threshold_percent: float = 80.0) -> list:
        """Return tenants approaching their quota. For admin alerts."""
        from files_management.models.file_quota import FileQuota

        results = []
        for quota in FileQuota.objects.select_related("website").all():
            if quota.usage_percent >= threshold_percent:
                results.append({
                    "website": str(quota.website),
                    "usage_percent": quota.usage_percent,
                    "current_size_bytes": quota.current_size_bytes,
                    "max_total_size_bytes": quota.max_total_size_bytes,
                    "remaining_bytes": quota.remaining_bytes,
                })
        return results
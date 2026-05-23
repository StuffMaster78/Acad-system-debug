"""
Subscriber Service
====================

Manages subscriber lifecycle: create, unsubscribe, import, cleanup.
"""

from __future__ import annotations

import csv
import logging
from io import StringIO

from django.utils import timezone

logger = logging.getLogger(__name__)


class SubscriberService:
    """Manage newsletter subscribers."""

    @classmethod
    def subscribe(
        cls,
        site,
        email: str,
        source: str = "blog_form",
        source_detail: str = "",
        consent_marketing: bool = False,
        frequency: str = "weekly",
    ) -> dict:
        """
        Subscribe an email address. Idempotent — reactivates if previously
        unsubscribed.

        Returns:
            {"created": bool, "reactivated": bool, "subscriber_id": int}
        """
        from cms_newsletters.models import Subscriber

        existing = Subscriber.objects.filter(site=site, email=email).first()

        if existing:
            if not existing.is_active:
                # Reactivate
                existing.is_active = True
                existing.unsubscribed_at = None
                existing.unsubscribe_reason = ""
                existing.consent_marketing = consent_marketing
                existing.consent_date = timezone.now()
                existing.save(update_fields=[
                    "is_active", "unsubscribed_at", "unsubscribe_reason",
                    "consent_marketing", "consent_date",
                ])
                logger.info("Reactivated subscriber: %s", email)
                return {
                    "created": False,
                    "reactivated": True,
                    "subscriber_id": existing.pk,
                }

            # Already active
            return {
                "created": False,
                "reactivated": False,
                "subscriber_id": existing.pk,
            }

        subscriber = Subscriber.objects.create(
            site=site,
            email=email,
            is_active=True,
            frequency=frequency,
            consent_marketing=consent_marketing,
            consent_date=timezone.now(),
            source=source,
            source_detail=source_detail,
        )

        logger.info("New subscriber: %s (source: %s)", email, source)
        return {
            "created": True,
            "reactivated": False,
            "subscriber_id": subscriber.pk,
        }

    @classmethod
    def unsubscribe(
        cls,
        site,
        email: str,
        reason: str = "other",
    ) -> bool:
        """
        Unsubscribe an email. Returns True if found and deactivated.
        """
        from cms_newsletters.models import Subscriber

        try:
            subscriber = Subscriber.objects.get(site=site, email=email)
            subscriber.is_active = False
            subscriber.unsubscribed_at = timezone.now()
            subscriber.unsubscribe_reason = reason
            subscriber.save(update_fields=[
                "is_active", "unsubscribed_at", "unsubscribe_reason",
            ])

            # Cancel active automation enrollments
            from cms_newsletters.models import AutomationEnrollment

            AutomationEnrollment.objects.filter(
                subscriber=subscriber,
                status="active",
            ).update(status="cancelled")

            logger.info("Unsubscribed: %s (reason: %s)", email, reason)
            return True

        except Exception:
            return False

    @classmethod
    def bulk_import(
        cls,
        site,
        csv_text: str,
        source: str = "import",
        source_detail: str = "",
    ) -> dict:
        """
        Import subscribers from CSV text.
        CSV must have at least an 'email' column.

        Returns:
            {"total": int, "created": int, "skipped": int, "errors": int}
        """
        from cms_newsletters.models import Subscriber

        reader = csv.DictReader(StringIO(csv_text))

        total = 0
        created = 0
        skipped = 0
        errors = 0

        for row in reader:
            total += 1
            email = row.get("email", "").strip().lower()

            if not email or "@" not in email:
                errors += 1
                continue

            try:
                result = cls.subscribe(
                    site=site,
                    email=email,
                    source=source,
                    source_detail=source_detail,
                )
                if result["created"]:
                    created += 1
                else:
                    skipped += 1
            except Exception as exc:
                errors += 1
                logger.warning("Import error for %s: %s", email, exc)

        logger.info(
            "Bulk import: %d total, %d created, %d skipped, %d errors",
            total, created, skipped, errors,
        )
        return {
            "total": total,
            "created": created,
            "skipped": skipped,
            "errors": errors,
        }

    @classmethod
    def cleanup_inactive(cls, site, inactive_days: int = 180) -> int:
        """
        Remove subscribers who haven't opened an email in N days
        and have been unsubscribed.

        Returns count of deleted subscribers.
        """
        from cms_newsletters.models import Subscriber

        cutoff = timezone.now() - timezone.timedelta(days=inactive_days)

        to_delete = Subscriber.objects.filter(
            site=site,
            is_active=False,
            unsubscribed_at__lte=cutoff,
        )

        count = to_delete.count()
        to_delete.delete()

        logger.info("Cleaned up %d inactive subscribers for %s", count, site.site_name)
        return count

    @classmethod
    def get_stats(cls, site) -> dict:
        """Subscriber statistics for the dashboard."""
        from django.db.models import Count, Q

        from cms_newsletters.models import Subscriber

        qs = Subscriber.objects.filter(site=site)

        stats = qs.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(is_active=True)),
            from_attachments=Count("id", filter=Q(source="attachment_gate")),
            from_blog=Count("id", filter=Q(source="blog_form")),
            from_orders=Count("id", filter=Q(source="order_optin")),
            from_import=Count("id", filter=Q(source="import")),
        )

        return stats
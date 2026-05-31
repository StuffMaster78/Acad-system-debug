"""
Freshness Scanner
===================

Nightly task that evaluates every published content page against
six freshness criteria and raises FreshnessAlert records.

Criteria:
1. Age threshold — last_substantive_update older than content-type threshold
2. Position decline — avg GSC position dropped 5+ over trailing 30 days
3. Click decline — GSC clicks dropped 30%+ over trailing 30 days
4. Engagement decline — GA4 engagement time dropped 25%+ over trailing 60 days
5. Editor flagged — manual flag (handled outside this scanner)
6. Topic event — external topic event (handled outside this scanner)

Celery beat::

    "scan-content-freshness": {
        "task": "cms_intelligence.tasks.freshness_scanner.scan_freshness",
        "schedule": crontab(hour=5, minute=0),
    }
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)

# Thresholds (configurable per content type)
AGE_THRESHOLDS = {
    "BlogPostPage": timedelta(days=365),    # 12 months
    "ServicePage": timedelta(days=180),      # 6 months
    "default": timedelta(days=365),
}

POSITION_DECLINE_THRESHOLD = 5.0   # positions lost
CLICK_DECLINE_THRESHOLD = 0.30     # 30% drop
ENGAGEMENT_DECLINE_THRESHOLD = 0.25  # 25% drop


@shared_task
def scan_freshness():
    """Run the freshness scanner across all published pages on all sites."""
    from wagtail.models import Page, Site

    results = []
    for site in Site.objects.all():
        try:
            result = _scan_site(site)
            results.append(result)
        except Exception as exc:
            logger.error("Freshness scan failed for %s: %s", site.site_name, exc)
            results.append({"site": site.site_name, "error": str(exc)})

    from cms_intelligence.tasks.sync_logger import log_sync

    total_alerts = sum(r.get("alerts_raised", 0) for r in results)
    total_resolved = sum(r.get("auto_resolved", 0) for r in results)
    errors = [r for r in results if "error" in r]
    status = "failed" if len(errors) == len(results) and results else (
        "partial" if errors else "success"
    )
    logger.info(
        "Freshness scan complete: %d new alerts, %d auto-resolved",
        total_alerts, total_resolved,
    )
    log_sync(
        task="freshness",
        status=status,
        rows_processed=total_alerts + total_resolved,
        error_message="; ".join(r.get("error", "") for r in errors) if errors else "",
    )
    return {"status": status, "alerts_raised": total_alerts, "auto_resolved": total_resolved}


def _scan_site(site) -> dict:
    """Scan all live pages under a site for freshness issues."""
    from wagtail.models import Page

    from cms_intelligence.models import ContentPerformanceSnapshot, FreshnessAlert

    now = timezone.now()
    alerts_raised = 0
    auto_resolved = 0

    live_pages = Page.objects.live().descendant_of(site.root_page, inclusive=False)

    for page in live_pages.specific().iterator(chunk_size=100):
        ct = ContentType.objects.get_for_model(page)
        page_type = page.__class__.__name__

        # Get the performance snapshot if it exists
        try:
            snapshot = ContentPerformanceSnapshot.objects.get(
                content_type=ct, object_id=page.pk,
            )
        except ContentPerformanceSnapshot.DoesNotExist:
            snapshot = None

        # --- Criterion 1: Age threshold ---
        last_update = getattr(page, "last_substantive_update", None)
        if last_update:
            threshold = AGE_THRESHOLDS.get(page_type, AGE_THRESHOLDS["default"])
            age = now - last_update
            if age > threshold:
                _raise_alert(
                    site=site,
                    ct=ct,
                    page=page,
                    alert_type="age_threshold",
                    severity=3,
                    detail={
                        "last_update": last_update.isoformat(),
                        "age_days": age.days,
                        "threshold_days": threshold.days,
                    },
                )
                alerts_raised += 1

        # --- Criterion 2: Position decline ---
        if snapshot and snapshot.position_delta > POSITION_DECLINE_THRESHOLD:
            _raise_alert(
                site=site,
                ct=ct,
                page=page,
                alert_type="position_decline",
                severity=4,
                detail={
                    "position_delta": snapshot.position_delta,
                    "current_position": snapshot.gsc_avg_position_30d,
                    "threshold": POSITION_DECLINE_THRESHOLD,
                },
            )
            alerts_raised += 1

        # --- Criterion 3: Click decline ---
        if snapshot and snapshot.clicks_delta_pct < -(CLICK_DECLINE_THRESHOLD * 100):
            _raise_alert(
                site=site,
                ct=ct,
                page=page,
                alert_type="click_decline",
                severity=3,
                detail={
                    "clicks_30d": snapshot.gsc_clicks_30d,
                    "clicks_delta_pct": snapshot.clicks_delta_pct,
                    "threshold_pct": CLICK_DECLINE_THRESHOLD * 100,
                },
            )
            alerts_raised += 1

        # --- Criterion 4: Engagement decline ---
        # Compare current 30d engagement to previous 30d
        if snapshot:
            try:
                from cms_intelligence.models import GA4DailyMetric

                d30 = (now - timedelta(days=30)).date()
                d60 = (now - timedelta(days=60)).date()
                page_path = page.url or f"/{page.slug}/"

                current_eng = GA4DailyMetric.objects.filter(
                    site=site, page_path=page_path, date__gte=d30,
                ).aggregate(avg=Avg("avg_engagement_seconds"))["avg"] or 0

                previous_eng = GA4DailyMetric.objects.filter(
                    site=site, page_path=page_path,
                    date__gte=d60, date__lt=d30,
                ).aggregate(avg=Avg("avg_engagement_seconds"))["avg"] or 0

                if previous_eng > 0:
                    eng_delta = (current_eng - previous_eng) / previous_eng
                    if eng_delta < -ENGAGEMENT_DECLINE_THRESHOLD:
                        _raise_alert(
                            site=site,
                            ct=ct,
                            page=page,
                            alert_type="engagement_decline",
                            severity=3,
                            detail={
                                "current_engagement_seconds": round(current_eng, 1),
                                "previous_engagement_seconds": round(previous_eng, 1),
                                "decline_pct": round(abs(eng_delta) * 100, 1),
                            },
                        )
                        alerts_raised += 1
            except Exception:
                pass

        # --- Auto-resolve stale alerts where condition recovered ---
        existing_alerts = FreshnessAlert.objects.filter(
            content_type=ct,
            object_id=page.pk,
            resolved_at__isnull=True,
        )
        for alert in existing_alerts:
            if _condition_recovered(alert, snapshot):
                alert.resolved_at = now
                alert.resolution = "auto_resolved"
                alert.save(update_fields=["resolved_at", "resolution"])
                auto_resolved += 1

    return {
        "site": site.site_name,
        "alerts_raised": alerts_raised,
        "auto_resolved": auto_resolved,
    }


def _raise_alert(site, ct, page, alert_type, severity, detail):
    """Create a FreshnessAlert if one doesn't already exist for this condition."""
    from cms_intelligence.models import FreshnessAlert

    existing = FreshnessAlert.objects.filter(
        content_type=ct,
        object_id=page.pk,
        alert_type=alert_type,
        resolved_at__isnull=True,
    ).first()

    if existing:
        # Update the detail data but don't duplicate
        existing.detail = detail
        existing.severity = max(existing.severity, severity)
        existing.save(update_fields=["detail", "severity"])
        return

    FreshnessAlert.objects.create(
        site=site,
        content_type=ct,
        object_id=page.pk,
        alert_type=alert_type,
        severity=severity,
        detail=detail,
    )


def _condition_recovered(alert, snapshot) -> bool:
    """Check if the condition that raised an alert has self-resolved."""
    if not snapshot:
        return False

    if alert.alert_type == "position_decline":
        return snapshot.position_delta <= 2.0  # recovered to within 2 positions

    if alert.alert_type == "click_decline":
        return snapshot.clicks_delta_pct >= -10  # clicks recovered to within 10% of baseline

    return False

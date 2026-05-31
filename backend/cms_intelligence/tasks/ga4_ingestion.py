"""
Google Analytics 4 Ingestion
===============================

Nightly Celery task that pulls engagement data from GA4
for each tenant via the GA4 Data API.

Celery beat schedule::

    "pull-ga4-data": {
        "task": "cms_intelligence.tasks.ga4_ingestion.pull_ga4_data",
        "schedule": crontab(hour=3, minute=30),  # 03:30 UTC daily
    }
"""

import logging
from datetime import date, timedelta

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)

BACKFILL_DAYS = 3  # GA4 data arrives faster than GSC


@shared_task
def pull_ga4_data():
    """Pull GA4 data for all tenants with configured GA4 properties."""
    from wagtail.models import Site

    from cms_core.models import TenantSEOSettings

    results = []

    for site in Site.objects.all():
        try:
            seo_settings = TenantSEOSettings.for_site(site)
        except Exception:
            continue

        if not seo_settings.ga4_property_id:
            logger.debug("Site %s has no GA4 property configured — skipping", site.site_name)
            continue

        try:
            result = _pull_ga4_for_site(site, seo_settings)
            results.append(result)
        except Exception as exc:
            logger.error("GA4 pull failed for %s: %s", site.site_name, exc)
            results.append({"site": site.site_name, "error": str(exc)})

    from cms_intelligence.tasks.sync_logger import log_sync

    total_rows = sum(r.get("rows_stored", 0) for r in results)
    errors = [r for r in results if "error" in r]
    status = "failed" if len(errors) == len(results) and results else (
        "partial" if errors else "success"
    )
    logger.info(
        "GA4 ingestion complete: %d sites, %d total rows",
        len(results),
        total_rows,
    )
    for r in results:
        log_sync(
            task="ga4",
            status="failed" if "error" in r else "success",
            rows_processed=r.get("rows_stored", 0),
            error_message=r.get("error", ""),
        )
    return {"status": status, "sites": len(results), "rows": total_rows}


def _pull_ga4_for_site(site, seo_settings) -> dict:
    """Pull GA4 data for a single tenant."""
    from cms_intelligence.models import GA4DailyMetric

    service_account_path = getattr(settings, "GA4_SERVICE_ACCOUNT_JSON", None)
    if not service_account_path:
        return {"site": site.site_name, "error": "No GA4 service account configured"}

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )

        client = BetaAnalyticsDataClient.from_service_account_json(
            service_account_path
        )
    except ImportError:
        logger.error(
            "google-analytics-data not installed. "
            "Install with: pip install google-analytics-data"
        )
        return {"site": site.site_name, "error": "Missing GA4 package"}
    except Exception as exc:
        return {"site": site.site_name, "error": f"Auth failed: {exc}"}

    rows_stored = 0
    today = date.today()

    for days_ago in range(BACKFILL_DAYS, 0, -1):
        pull_date = today - timedelta(days=days_ago)
        date_str = pull_date.isoformat().replace("-", "")  # GA4 uses YYYYMMDD

        try:
            request = RunReportRequest(
                property=f"properties/{seo_settings.ga4_property_id}",
                date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
                dimensions=[
                    Dimension(name="pagePath"),
                    Dimension(name="sessionDefaultChannelGroup"),
                ],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="sessions"),
                    Metric(name="engagedSessions"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="conversions"),
                ],
            )

            response = client.run_report(request)

            for row in response.rows:
                page_path = row.dimension_values[0].value
                channel = row.dimension_values[1].value

                GA4DailyMetric.objects.update_or_create(
                    site=site,
                    date=pull_date,
                    page_path=page_path,
                    channel=channel,
                    defaults={
                        "page_views": int(row.metric_values[0].value or 0),
                        "sessions": int(row.metric_values[1].value or 0),
                        "engaged_sessions": int(row.metric_values[2].value or 0),
                        "avg_engagement_seconds": float(row.metric_values[3].value or 0),
                        "conversions": int(row.metric_values[4].value or 0),
                    },
                )
                rows_stored += 1

        except Exception as exc:
            logger.warning(
                "GA4 pull for %s on %s failed: %s",
                site.site_name,
                pull_date.isoformat(),
                exc,
            )
            continue

    logger.info(
        "GA4 data pulled for %s: %d rows",
        site.site_name,
        rows_stored,
    )
    return {"site": site.site_name, "rows_stored": rows_stored}

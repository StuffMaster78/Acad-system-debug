"""
Google Search Console Ingestion
=================================

Nightly Celery task that pulls search analytics data from GSC
for each tenant and stores it in GSCDailyMetric rows.

Resolves page paths to content nodes during ingestion.

Configuration per tenant:
    TenantSEOSettings.gsc_property_url — the GSC property URL
    Service account credentials in settings.GSC_SERVICE_ACCOUNT_JSON

Celery beat schedule::

    "pull-gsc-data": {
        "task": "cms_intelligence.tasks.gsc_ingestion.pull_gsc_data",
        "schedule": crontab(hour=3, minute=0), # 03:00 UTC daily
    }
"""

import logging
from datetime import date, timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Re-pull the last N days to account for GSC's data backfill lag
BACKFILL_DAYS = 7


@shared_task
def pull_gsc_data():
    """Pull GSC data for all tenants with configured GSC properties."""
    from wagtail.models import Site

    from cms_core.models import TenantSEOSettings

    results = []

    for site in Site.objects.all():
        try:
            seo_settings = TenantSEOSettings.for_site(site)
        except Exception:
            continue

        if not seo_settings.gsc_property_url:
            logger.debug("Site %s has no GSC property configured — skipping", site.site_name)
            continue

        try:
            result = _pull_gsc_for_site(site, seo_settings)
            results.append(result)
        except Exception as exc:
            logger.error(
                "GSC pull failed for %s: %s",
                site.site_name,
                exc,
            )
            results.append({
                "site": site.site_name,
                "error": str(exc),
            })

    from cms_intelligence.tasks.sync_logger import log_sync

    total_rows = sum(r.get("rows_stored", 0) for r in results)
    errors = [r for r in results if "error" in r]
    status = "failed" if len(errors) == len(results) and results else (
        "partial" if errors else "success"
    )
    logger.info(
        "GSC ingestion complete: %d sites, %d total rows stored",
        len(results),
        total_rows,
    )
    for r in results:
        log_sync(
            task="gsc",
            site=None,
            status="failed" if "error" in r else "success",
            rows_processed=r.get("rows_stored", 0),
            error_message=r.get("error", ""),
        )
    return {"status": status, "sites": len(results), "rows": total_rows}


def _pull_gsc_for_site(site, seo_settings) -> dict:
    """Pull GSC data for a single tenant site."""
    from cms_intelligence.models import GSCDailyMetric

    service_account_path = getattr(settings, "GSC_SERVICE_ACCOUNT_JSON", None)
    if not service_account_path:
        logger.warning("GSC_SERVICE_ACCOUNT_JSON not configured in settings")
        return {"site": site.site_name, "error": "No service account configured"}

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        sc_service = build("searchconsole", "v1", credentials=credentials)
    except ImportError:
        logger.error(
            "google-api-python-client or google-auth not installed. "
            "Install with: pip install google-api-python-client google-auth"
        )
        return {"site": site.site_name, "error": "Missing Google API packages"}
    except Exception as exc:
        return {"site": site.site_name, "error": f"Auth failed: {exc}"}

    rows_stored = 0
    today = date.today()

    for days_ago in range(BACKFILL_DAYS, 0, -1):
        pull_date = today - timedelta(days=days_ago)
        date_str = pull_date.isoformat()

        try:
            response = (
                sc_service.searchanalytics()
                .query(
                    siteUrl=seo_settings.gsc_property_url,
                    body={
                        "startDate": date_str,
                        "endDate": date_str,
                        "dimensions": ["query", "page"],
                        "rowLimit": 25000,
                        "dataState": "final",
                    },
                )
                .execute()
            )

            for row in response.get("rows", []):
                keys = row.get("keys", [])
                if len(keys) < 2:
                    continue

                query = keys[0]
                page_url = keys[1]

                # Extract path from full URL
                from urllib.parse import urlparse

                page_path = urlparse(page_url).path

                GSCDailyMetric.objects.update_or_create(
                    site=site,
                    date=pull_date,
                    page_path=page_path,
                    query=query,
                    defaults={
                        "clicks": int(row.get("clicks", 0)),
                        "impressions": int(row.get("impressions", 0)),
                        "ctr": float(row.get("ctr", 0.0)),
                        "position": float(row.get("position", 0.0)),
                    },
                )
                rows_stored += 1

        except Exception as exc:
            logger.warning(
                "GSC pull for %s on %s failed: %s",
                site.site_name,
                date_str,
                exc,
            )
            continue

    # Resolve page paths to content nodes
    _resolve_gsc_pages(site)

    logger.info(
        "GSC data pulled for %s: %d rows across %d days",
        site.site_name,
        rows_stored,
        BACKFILL_DAYS,
    )
    return {"site": site.site_name, "rows_stored": rows_stored}


def _resolve_gsc_pages(site):
    """Resolve GSC page_path values to content node FKs."""
    from django.contrib.contenttypes.models import ContentType

    from wagtail.models import Page

    from cms_intelligence.models import GSCDailyMetric

    unresolved = GSCDailyMetric.objects.filter(
        site=site,
        resolved_page_content_type__isnull=True,
    ).values_list("page_path", flat=True).distinct()

    for path in unresolved:
        # Try to find a Wagtail page matching this path
        try:
            page = Page.objects.live().descendant_of(
                site.root_page, inclusive=True
            ).filter(url_path__endswith=path.rstrip("/") + "/").first()

            if page:
                ct = ContentType.objects.get_for_model(page.specific_class)
                GSCDailyMetric.objects.filter(
                    site=site,
                    page_path=path,
                    resolved_page_content_type__isnull=True,
                ).update(
                    resolved_page_content_type=ct,
                    resolved_page_object_id=page.pk,
                )
        except Exception:
            continue
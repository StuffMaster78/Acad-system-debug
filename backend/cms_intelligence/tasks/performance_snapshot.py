"""
Performance Snapshot Computation
==================================

Nightly task that materializes ContentPerformanceSnapshot for every
published content page. Aggregates GSC + GA4 + internal conversion data
into a single pre-computed row per page for fast dashboard queries.

Also runs the diagnostic categorizer to label underperformers.

Celery beat::

    "compute-performance-snapshots": {
        "task": "cms_intelligence.tasks.performance_snapshot.compute_performance_snapshots",
        "schedule": crontab(hour=4, minute=0),
    }
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def compute_performance_snapshots():
    """Compute performance snapshots for all published pages across all sites."""
    from wagtail.models import Page, Site

    results = []
    for site in Site.objects.all():
        try:
            result = _compute_for_site(site)
            results.append(result)
        except Exception as exc:
            logger.error("Snapshot computation failed for %s: %s", site.site_name, exc)
            results.append({"site": site.site_name, "error": str(exc)})

    total = sum(r.get("pages_updated", 0) for r in results)
    logger.info("Performance snapshots computed: %d pages across %d sites", total, len(results))
    return results


def _compute_for_site(site) -> dict:
    """Compute snapshots for all live pages under a site."""
    from wagtail.models import Page

    from cms_intelligence.models import (
        ContentPerformanceSnapshot,
        GA4DailyMetric,
        GSCDailyMetric,
    )

    now = timezone.now()
    d30_ago = (now - timedelta(days=30)).date()
    d60_ago = (now - timedelta(days=60)).date()
    d90_ago = (now - timedelta(days=90)).date()

    live_pages = Page.objects.live().descendant_of(site.root_page, inclusive=False)
    updated = 0

    for page in live_pages.specific().iterator(chunk_size=100):
        ct = ContentType.objects.get_for_model(page)
        page_path = page.url or f"/{page.slug}/"

        # --- GSC 30d ---
        gsc_30d = GSCDailyMetric.objects.filter(
            site=site, page_path=page_path, date__gte=d30_ago,
        ).aggregate(
            clicks=Sum("clicks"),
            impressions=Sum("impressions"),
            avg_position=Avg("position"),
            avg_ctr=Avg("ctr"),
        )

        # --- GSC 90d ---
        gsc_90d = GSCDailyMetric.objects.filter(
            site=site, page_path=page_path, date__gte=d90_ago,
        ).aggregate(clicks=Sum("clicks"))

        # --- GSC previous 30d (for delta) ---
        gsc_prev = GSCDailyMetric.objects.filter(
            site=site, page_path=page_path,
            date__gte=d60_ago, date__lt=d30_ago,
        ).aggregate(
            clicks=Sum("clicks"),
            avg_position=Avg("position"),
        )

        # --- GA4 30d ---
        ga4_30d = GA4DailyMetric.objects.filter(
            site=site, page_path=page_path, date__gte=d30_ago,
        ).aggregate(
            page_views=Sum("page_views"),
            sessions=Sum("sessions"),
            avg_engagement=Avg("avg_engagement_seconds"),
        )

        # --- GA4 90d ---
        ga4_90d = GA4DailyMetric.objects.filter(
            site=site, page_path=page_path, date__gte=d90_ago,
        ).aggregate(page_views=Sum("page_views"))

        # --- AI Overview appearances ---
        ai_overview_count = GSCDailyMetric.objects.filter(
            site=site, page_path=page_path,
            date__gte=d30_ago, appeared_in_ai_overview=True,
        ).count()

        # --- Conversions (from cms_engagement or orders) ---
        conversions_30d = 0
        revenue_30d = 0
        try:
            from cms_intelligence.models import ConversionAttribution

            conv_data = ConversionAttribution.objects.filter(
                content_type=ct,
                object_id=page.pk,
                attribution_model="last_touch",
                created_at__gte=now - timedelta(days=30),
            ).aggregate(
                total_conversions=Sum("credit_share"),
                total_revenue=Sum("attributed_revenue"),
            )
            conversions_30d = int(conv_data["total_conversions"] or 0)
            revenue_30d = conv_data["total_revenue"] or 0
        except Exception:
            pass

        # --- Deltas ---
        clicks_current = gsc_30d["clicks"] or 0
        clicks_previous = gsc_prev["clicks"] or 0
        if clicks_previous > 0:
            clicks_delta_pct = ((clicks_current - clicks_previous) / clicks_previous) * 100
        else:
            clicks_delta_pct = 0.0

        position_current = gsc_30d["avg_position"] or 0
        position_previous = gsc_prev["avg_position"] or 0
        position_delta = position_current - position_previous  # positive = worsened

        # --- Diagnosis ---
        diagnosis = _diagnose(
            impressions=gsc_30d["impressions"] or 0,
            ctr=gsc_30d["avg_ctr"] or 0,
            avg_engagement=ga4_30d["avg_engagement"] or 0,
            page_views=ga4_30d["page_views"] or 0,
            conversions=conversions_30d,
            position_delta=position_delta,
        )

        # --- Upsert ---
        ContentPerformanceSnapshot.objects.update_or_create(
            content_type=ct,
            object_id=page.pk,
            defaults={
                "site": site,
                "page_title": page.title,
                "page_slug": page.slug,
                "gsc_clicks_30d": clicks_current,
                "gsc_impressions_30d": gsc_30d["impressions"] or 0,
                "gsc_avg_position_30d": round(position_current, 1),
                "gsc_avg_ctr_30d": round(gsc_30d["avg_ctr"] or 0, 4),
                "ga4_page_views_30d": ga4_30d["page_views"] or 0,
                "ga4_sessions_30d": ga4_30d["sessions"] or 0,
                "ga4_avg_engagement_30d": round(ga4_30d["avg_engagement"] or 0, 1),
                "gsc_clicks_90d": gsc_90d["clicks"] or 0,
                "ga4_page_views_90d": ga4_90d["page_views"] or 0,
                "clicks_delta_pct": round(clicks_delta_pct, 1),
                "position_delta": round(position_delta, 1),
                "internal_conversions_30d": conversions_30d,
                "attributed_revenue_30d": revenue_30d,
                "ai_overview_appearances_30d": ai_overview_count,
                "diagnosis": diagnosis,
            },
        )
        updated += 1

    return {"site": site.site_name, "pages_updated": updated}


def _diagnose(
    impressions: int,
    ctr: float,
    avg_engagement: float,
    page_views: int,
    conversions: int,
    position_delta: float,
) -> str:
    """Categorize a page's performance into a diagnosis bucket."""

    if position_delta > 5:
        return "declining_position"

    if impressions > 100 and ctr < 0.02:
        return "low_ctr"

    if page_views > 50 and avg_engagement < 30:
        return "low_engagement"

    if page_views > 100 and conversions == 0:
        return "no_conversion_path"

    if impressions < 10:
        return "not_visible"

    return "healthy"
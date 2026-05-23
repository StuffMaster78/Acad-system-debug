"""
Performance Diagnostics Service
==================================

Categorizes underperforming pages by pattern and suggests actions.

Patterns:
- low_ctr: high impressions + low CTR → rewrite title/meta description
- low_engagement: high CTR + low engagement → page over-promised
- no_conversion_path: traffic but no conversions → add CTAs
- declining_position: position dropping → refresh content
- not_visible: no impressions → check indexation
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cms_intelligence.models import ContentPerformanceSnapshot

logger = logging.getLogger(__name__)


class PerformanceDiagnosticService:
    """Diagnose underperforming content and suggest actions."""

    @staticmethod
    def diagnose(snapshot: ContentPerformanceSnapshot) -> dict:
        """
        Analyze a performance snapshot and return a diagnosis.

        Returns:
            {
                "category": str,
                "severity": "none" | "low" | "medium" | "high" | "critical",
                "title": str,
                "action": str,
                "metrics": dict,
            }
        """

        # Priority 1: Declining position (most urgent — active loss)
        if snapshot.position_delta > 5:
            severity = (
                "critical" if snapshot.position_delta > 15
                else "high" if snapshot.position_delta > 10
                else "medium"
            )
            return {
                "category": "declining_position",
                "severity": severity,
                "title": "Search position declining",
                "action": (
                    "This page lost ranking. Check freshness alerts, "
                    "review competing content for the same queries, "
                    "and consider a substantive content refresh."
                ),
                "metrics": {
                    "position_delta": round(snapshot.position_delta, 1),
                    "current_position": round(snapshot.gsc_avg_position_30d, 1),
                },
            }

        # Priority 2: High impressions + low CTR (opportunity being wasted)
        if (
            snapshot.gsc_impressions_30d > 100
            and snapshot.gsc_avg_ctr_30d < 0.02
        ):
            return {
                "category": "low_ctr",
                "severity": "high",
                "title": "High impressions but low click-through rate",
                "action": (
                    "This page appears in search results but few people click. "
                    "Rewrite the meta title and description for better SERP appeal. "
                    "Consider if the title matches search intent."
                ),
                "metrics": {
                    "impressions_30d": snapshot.gsc_impressions_30d,
                    "ctr": round(snapshot.gsc_avg_ctr_30d * 100, 2),
                    "clicks_30d": snapshot.gsc_clicks_30d,
                },
            }

        # Priority 3: Traffic but low engagement (content disappoints)
        if (
            snapshot.ga4_page_views_30d > 50
            and snapshot.ga4_avg_engagement_30d < 30
        ):
            return {
                "category": "low_engagement",
                "severity": "high",
                "title": "Visitors arrive but don't engage",
                "action": (
                    "Users click through but leave quickly. "
                    "The page may over-promise in its title/description "
                    "or underdeliver on content quality. "
                    "Review the intro, structure, and value proposition."
                ),
                "metrics": {
                    "page_views_30d": snapshot.ga4_page_views_30d,
                    "avg_engagement_seconds": round(snapshot.ga4_avg_engagement_30d, 1),
                },
            }

        # Priority 4: Traffic but no conversions (missing funnel)
        if (
            snapshot.ga4_page_views_30d > 100
            and snapshot.internal_conversions_30d == 0
        ):
            return {
                "category": "no_conversion_path",
                "severity": "medium",
                "title": "Traffic but no conversions",
                "action": (
                    "This page gets traffic but no visitors convert. "
                    "Add a clear CTA linking to a service page, "
                    "ensure the blog→service route is configured, "
                    "and consider adding a lead magnet or email capture."
                ),
                "metrics": {
                    "page_views_30d": snapshot.ga4_page_views_30d,
                    "conversions_30d": 0,
                },
            }

        # Priority 5: No visibility at all
        if snapshot.gsc_impressions_30d < 10:
            return {
                "category": "not_visible",
                "severity": "medium",
                "title": "Not appearing in search results",
                "action": (
                    "This page has almost no search impressions. "
                    "Check if it's indexed (search site:domain.com/slug). "
                    "Reconsider the target keyword — it may be too competitive "
                    "or the topic may not have search demand."
                ),
                "metrics": {
                    "impressions_30d": snapshot.gsc_impressions_30d,
                },
            }

        # Healthy
        return {
            "category": "healthy",
            "severity": "none",
            "title": "Performing normally",
            "action": None,
            "metrics": {
                "clicks_30d": snapshot.gsc_clicks_30d,
                "page_views_30d": snapshot.ga4_page_views_30d,
                "conversions_30d": snapshot.internal_conversions_30d,
            },
        }

    @classmethod
    def diagnose_all_for_site(cls, site) -> dict:
        """
        Run diagnostics on all content for a site.

        Returns:
            {
                "total_pages": int,
                "healthy": int,
                "by_category": {
                    "low_ctr": [{"page_title": ..., "action": ...}, ...],
                    "declining_position": [...],
                    ...
                }
            }
        """
        from cms_intelligence.models import ContentPerformanceSnapshot

        snapshots = ContentPerformanceSnapshot.objects.filter(site=site)

        results = {
            "total_pages": snapshots.count(),
            "healthy": 0,
            "by_category": {},
        }

        for snapshot in snapshots:
            diagnosis = cls.diagnose(snapshot)
            category = diagnosis["category"]

            if category == "healthy":
                results["healthy"] += 1
                continue

            if category not in results["by_category"]:
                results["by_category"][category] = []

            results["by_category"][category].append({
                "page_title": snapshot.page_title,
                "page_slug": snapshot.page_slug,
                "severity": diagnosis["severity"],
                "action": diagnosis["action"],
                "metrics": diagnosis["metrics"],
            })

        # Sort each category by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for category in results["by_category"]:
            results["by_category"][category].sort(
                key=lambda x: severity_order.get(x["severity"], 99)
            )

        return results

    @classmethod
    def get_summary_for_dashboard(cls, site) -> dict:
        """
        Compact summary for the admin dashboard header.

        Returns:
            {
                "total_pages": int,
                "healthy": int,
                "needs_attention": int,
                "critical": int,
                "top_issues": [
                    {"category": "low_ctr", "count": 23, "label": "Low CTR"},
                    ...
                ]
            }
        """
        full = cls.diagnose_all_for_site(site)

        needs_attention = sum(
            len(pages) for pages in full["by_category"].values()
        )
        critical = sum(
            len([p for p in pages if p["severity"] == "critical"])
            for pages in full["by_category"].values()
        )

        labels = {
            "low_ctr": "Low CTR — title rewrites needed",
            "low_engagement": "Low engagement — content review needed",
            "no_conversion_path": "No conversion path — add CTAs",
            "declining_position": "Declining positions — refresh needed",
            "not_visible": "Not visible — indexation check needed",
        }

        top_issues = [
            {
                "category": cat,
                "count": len(pages),
                "label": labels.get(cat, cat),
            }
            for cat, pages in sorted(
                full["by_category"].items(),
                key=lambda x: -len(x[1]),
            )
        ]

        return {
            "total_pages": full["total_pages"],
            "healthy": full["healthy"],
            "needs_attention": needs_attention,
            "critical": critical,
            "top_issues": top_issues,
        }
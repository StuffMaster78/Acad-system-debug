"""
Funnel Analytics Service
==========================

End-to-end funnel reporting per service/pillar.

Answers:
- For each service, how is its funnel performing?
- Where is the funnel leaking?
- Which blog→service routes convert best?
- What's the revenue per blog visitor for each pillar?
"""

from __future__ import annotations

import logging
from decimal import Decimal

from django.db.models import Avg, F, Sum

logger = logging.getLogger(__name__)


class FunnelAnalyticsService:
    """Compute end-to-end funnel metrics per ContentPillar."""

    @classmethod
    def get_funnel_report(cls, pillar) -> dict:
        """
        Full funnel report for a single ContentPillar.

        Returns:
            {
                "pillar": {"name", "slug"},
                "service_page": {"title", "slug", "url"},
                "hub_post": {"title", "slug", "url"} or None,
                "top_of_funnel": {
                    "spoke_count": int,
                    "total_traffic_30d": int,
                    "hub_traffic_30d": int,
                },
                "middle": {
                    "total_blog_to_service_clicks": int,
                    "click_through_rate": float,
                    "best_route": {...} or None,
                    "worst_route": {...} or None,
                },
                "bottom": {
                    "service_page_sessions": int,
                    "orders": int,
                    "conversion_rate": float,
                    "revenue": Decimal,
                },
                "efficiency": {
                    "revenue_per_blog_visitor": float,
                },
            }
        """
        from cms_content_graph.models import BlogServiceLink
        from cms_intelligence.models import ContentPerformanceSnapshot

        report = {
            "pillar": {
                "name": pillar.name,
                "slug": pillar.slug,
            },
            "service_page": {
                "title": pillar.service_page.title,
                "slug": pillar.service_page.slug,
                "url": pillar.service_page.url,
            },
        }

        # Hub
        if pillar.hub_post:
            report["hub_post"] = {
                "title": pillar.hub_post.title,
                "slug": pillar.hub_post.slug,
                "url": pillar.hub_post.url,
            }
        else:
            report["hub_post"] = None

        # --- Top of funnel ---
        spoke_posts = pillar.spoke_posts
        spoke_count = spoke_posts.count()

        spoke_traffic = 0
        hub_traffic = 0

        from django.contrib.contenttypes.models import ContentType

        for post in spoke_posts:
            try:
                ct = ContentType.objects.get_for_model(post)
                snapshot = ContentPerformanceSnapshot.objects.filter(
                    content_type=ct, object_id=post.pk,
                ).first()
                if snapshot:
                    spoke_traffic += snapshot.ga4_page_views_30d
            except Exception:
                continue

        if pillar.hub_post:
            try:
                ct = ContentType.objects.get_for_model(pillar.hub_post)
                hub_snapshot = ContentPerformanceSnapshot.objects.filter(
                    content_type=ct, object_id=pillar.hub_post.pk,
                ).first()
                if hub_snapshot:
                    hub_traffic = hub_snapshot.ga4_page_views_30d
            except Exception:
                pass

        total_top_traffic = spoke_traffic + hub_traffic

        report["top_of_funnel"] = {
            "spoke_count": spoke_count,
            "total_traffic_30d": total_top_traffic,
            "hub_traffic_30d": hub_traffic,
        }

        # --- Middle (blog → service routes) ---
        routes = BlogServiceLink.objects.filter(
            service_page=pillar.service_page,
        )

        total_clicks = routes.aggregate(total=Sum("clicks"))["total"] or 0
        total_impressions = routes.aggregate(total=Sum("impressions"))["total"] or 0
        route_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0

        best_route = routes.order_by("-clicks").first()
        worst_route = routes.filter(impressions__gt=100).order_by("clicks").first()

        middle = {
            "total_blog_to_service_clicks": total_clicks,
            "click_through_rate": round(route_ctr, 2),
            "routes_count": routes.count(),
        }

        if best_route:
            middle["best_route"] = {
                "blog_title": best_route.blog_post.title,
                "clicks": best_route.clicks,
                "ctr": round(best_route.ctr, 1),
                "placement": best_route.placement,
            }

        if worst_route and worst_route != best_route:
            middle["worst_route"] = {
                "blog_title": worst_route.blog_post.title,
                "clicks": worst_route.clicks,
                "ctr": round(worst_route.ctr, 1),
                "placement": worst_route.placement,
            }

        report["middle"] = middle

        # --- Bottom (service page → conversion) ---
        service_ct = ContentType.objects.get_for_model(pillar.service_page)
        service_snapshot = ContentPerformanceSnapshot.objects.filter(
            content_type=service_ct,
            object_id=pillar.service_page.pk,
        ).first()

        service_sessions = service_snapshot.ga4_sessions_30d if service_snapshot else 0
        conversions = service_snapshot.internal_conversions_30d if service_snapshot else 0
        revenue = service_snapshot.attributed_revenue_30d if service_snapshot else Decimal("0")

        conversion_rate = (
            (conversions / service_sessions * 100)
            if service_sessions > 0
            else 0.0
        )

        report["bottom"] = {
            "service_page_sessions": service_sessions,
            "orders": conversions,
            "conversion_rate": round(conversion_rate, 2),
            "revenue": revenue,
        }

        # --- Efficiency ---
        revenue_per_visitor = (
            float(revenue) / total_top_traffic
            if total_top_traffic > 0
            else 0.0
        )

        report["efficiency"] = {
            "revenue_per_blog_visitor": round(revenue_per_visitor, 4),
        }

        return report

    @classmethod
    def get_all_funnels_for_site(cls, site) -> list[dict]:
        """Get funnel reports for all pillars on a site, ranked by revenue."""
        from cms_content_graph.models import ContentPillar

        pillars = ContentPillar.objects.filter(site=site).select_related(
            "service_page", "hub_post",
        )

        reports = []
        for pillar in pillars:
            try:
                report = cls.get_funnel_report(pillar)
                reports.append(report)
            except Exception as exc:
                logger.warning(
                    "Funnel report failed for pillar %s: %s",
                    pillar.name,
                    exc,
                )

        # Sort by revenue descending
        reports.sort(
            key=lambda r: float(r["bottom"]["revenue"]),
            reverse=True,
        )
        return reports

    @classmethod
    def get_dashboard_summary(cls, site) -> dict:
        """
        Compact funnel summary for the admin dashboard.

        Returns:
            {
                "total_pillars": int,
                "total_revenue_30d": Decimal,
                "total_conversions_30d": int,
                "total_blog_traffic_30d": int,
                "avg_funnel_conversion_rate": float,
                "strongest_pillar": str or None,
                "weakest_pillar": str or None,
            }
        """
        reports = cls.get_all_funnels_for_site(site)

        if not reports:
            return {
                "total_pillars": 0,
                "total_revenue_30d": Decimal("0"),
                "total_conversions_30d": 0,
                "total_blog_traffic_30d": 0,
                "avg_funnel_conversion_rate": 0.0,
                "strongest_pillar": None,
                "weakest_pillar": None,
            }

        total_revenue = sum(
            float(r["bottom"]["revenue"]) for r in reports
        )
        total_conversions = sum(r["bottom"]["orders"] for r in reports)
        total_traffic = sum(
            r["top_of_funnel"]["total_traffic_30d"] for r in reports
        )
        conversion_rates = [
            r["bottom"]["conversion_rate"]
            for r in reports
            if r["bottom"]["service_page_sessions"] > 0
        ]
        avg_conv = (
            sum(conversion_rates) / len(conversion_rates)
            if conversion_rates
            else 0.0
        )

        return {
            "total_pillars": len(reports),
            "total_revenue_30d": Decimal(str(round(total_revenue, 2))),
            "total_conversions_30d": total_conversions,
            "total_blog_traffic_30d": total_traffic,
            "avg_funnel_conversion_rate": round(avg_conv, 2),
            "strongest_pillar": reports[0]["pillar"]["name"] if reports else None,
            "weakest_pillar": reports[-1]["pillar"]["name"] if len(reports) > 1 else None,
        }

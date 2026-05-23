"""
Nightly engagement aggregation.
Computes EngagementSummary for every content page.
"""

import logging

from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def compute_engagement_summaries():
    """
    Nightly task: recompute EngagementSummary for every page
    that has at least one PageView.

    Aggregates from raw event tables into the materialized summary.
    """
    from cms_engagement.models import (
        EngagementSummary,
        PageReaction,
        PageShare,
        PageView,
    )

    # Get all distinct (content_type, object_id) pairs from PageView
    distinct_pages = (
        PageView.objects.values("content_type", "object_id", "site")
        .distinct()
    )

    updated = 0
    for entry in distinct_pages.iterator():
        ct_id = entry["content_type"]
        obj_id = entry["object_id"]
        site_id = entry["site"]

        try:
            ct = ContentType.objects.get(pk=ct_id)
        except ContentType.DoesNotExist:
            continue

        # --- Views ---
        views_qs = PageView.objects.filter(
            content_type_id=ct_id,
            object_id=obj_id,
        )
        view_aggs = views_qs.aggregate(
            total=Count("id"),
            unique=Count("session_id", distinct=True),
            avg_time=Avg("time_on_page"),
            avg_scroll=Avg("scroll_depth"),
        )
        total_views = view_aggs["total"] or 0
        unique_views = view_aggs["unique"] or 0
        avg_time = view_aggs["avg_time"] or 0.0
        avg_scroll = view_aggs["avg_scroll"] or 0.0

        # Bounce rate: % of views with scroll_depth < 25
        if total_views > 0:
            bounces = views_qs.filter(scroll_depth__lt=25).count()
            bounce_rate = (bounces / total_views) * 100
        else:
            bounce_rate = 0.0

        # --- Reactions ---
        reactions = PageReaction.objects.filter(
            content_type_id=ct_id,
            object_id=obj_id,
        )
        thumbs_up = reactions.filter(reaction_type="thumbs_up").count()
        thumbs_down = reactions.filter(reaction_type="thumbs_down").count()
        love = reactions.filter(reaction_type="love").count()
        useful = reactions.filter(reaction_type="useful").count()

        total_positive = thumbs_up + love + useful
        total_reactions = total_positive + thumbs_down
        helpfulness = (
            total_positive / total_reactions if total_reactions > 0 else 0.0
        )

        # --- Shares ---
        total_shares = PageShare.objects.filter(
            content_type_id=ct_id,
            object_id=obj_id,
        ).count()

        # --- Engagement score (0-100) ---
        # Weighted formula: views (30%) + time (20%) + scroll (20%) +
        # reactions (15%) + shares (15%)
        view_score = min(total_views / 100, 1.0) * 30
        time_score = min(avg_time / 300, 1.0) * 20  # 5 min = max
        scroll_score = (avg_scroll / 100) * 20
        reaction_score = min(total_reactions / 50, 1.0) * 15
        share_score = min(total_shares / 20, 1.0) * 15
        engagement_score = int(
            view_score + time_score + scroll_score
            + reaction_score + share_score
        )

        # --- Upsert ---
        summary, created = EngagementSummary.objects.update_or_create(
            content_type_id=ct_id,
            object_id=obj_id,
            defaults={
                "site_id": site_id,
                "total_views": total_views,
                "unique_views": unique_views,
                "avg_time_on_page": round(avg_time, 1),
                "avg_scroll_depth": round(avg_scroll, 1),
                "bounce_rate": round(bounce_rate, 1),
                "thumbs_up_count": thumbs_up,
                "thumbs_down_count": thumbs_down,
                "love_count": love,
                "useful_count": useful,
                "total_shares": total_shares,
                "engagement_score": engagement_score,
                "helpfulness_ratio": round(helpfulness, 3),
            },
        )
        updated += 1

    logger.info("Engagement summaries computed for %d pages", updated)
    return {"pages_updated": updated}
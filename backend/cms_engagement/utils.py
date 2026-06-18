"""
Engagement prefetch utility.

Call prefetch_engagement(pages) before serializing any page listing that
reads views_count or likes_count to avoid N+1 queries.  The function
fetches all relevant EngagementSummary rows in a single query and caches
them on each page object as _cached_engagement.
"""

from __future__ import annotations

from typing import Sequence


def prefetch_engagement(pages: Sequence) -> Sequence:
    """
    Bulk-attach EngagementSummary to each page in one extra query.

    Sets ``page._cached_engagement`` to the matching summary or ``None``.
    The BlogPostPage properties ``views_count`` and ``likes_count`` check
    this attribute before falling back to per-object DB lookups.
    """
    from django.contrib.contenttypes.models import ContentType
    from cms_engagement.models import EngagementSummary

    page_list = list(pages)
    if not page_list:
        return page_list

    # Group pages by their concrete model class so we send one query per type.
    by_ct: dict[int, list] = {}
    ct_cache: dict[type, int] = {}

    for page in page_list:
        cls = page.__class__
        if cls not in ct_cache:
            ct_cache[cls] = ContentType.objects.get_for_model(cls).pk
        ct_id = ct_cache[cls]
        by_ct.setdefault(ct_id, []).append(page)

    for ct_id, group in by_ct.items():
        pk_to_summary: dict[int, object] = {p.pk: None for p in group}
        for summary in EngagementSummary.objects.filter(
            content_type_id=ct_id,
            object_id__in=pk_to_summary,
        ):
            pk_to_summary[summary.object_id] = summary

        for page in group:
            page._cached_engagement = pk_to_summary.get(page.pk)
            page._engagement_prefetched = True

    return page_list

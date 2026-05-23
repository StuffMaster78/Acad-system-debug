"""
Internal Linking Service
==========================

Three jobs:
1. SUGGEST — during composition, surface relevant internal content to link to
2. VALIDATE — on publish, check linking health
3. MAINTAIN — weekly scans for orphans and dead ends

This is the "content graph brain" that makes the platform's linking
intelligence work.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db.models import Count, Q

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class InternalLinkingService:
    """Suggest, validate, and maintain internal links."""

    # ------------------------------------------------------------------
    # 1. SUGGEST — called by the composer
    # ------------------------------------------------------------------

    @classmethod
    def suggest_links_for_page(cls, page, max_suggestions: int = 10) -> list[dict]:
        """
        Given a blog post (or service page), return ranked suggestions
        for internal links.

        Suggestion sources (in priority order):
        1. Hub page of the post's pillar
        2. Service page the post routes to
        3. Other spoke posts in the same pillar
        4. Embedding similarity (if embeddings exist)
        5. Same-category posts

        Returns list of dicts:
            [{"page_id": int, "title": str, "url": str,
              "reason": str, "score": float}, ...]
        """
        from cms_blog.models import BlogPostPage

        suggestions = []
        seen_ids = {page.pk}

        site = page.get_site()
        if not site:
            return []

        # --- 1. Pillar hub ---
        pillar = getattr(page, "pillar", None)
        if pillar and pillar.hub_post and pillar.hub_post.pk not in seen_ids:
            hub = pillar.hub_post
            if hub.live:
                suggestions.append({
                    "page_id": hub.pk,
                    "title": hub.title,
                    "url": hub.url,
                    "reason": f"Hub for pillar: {pillar.name}",
                    "score": 0.95,
                })
                seen_ids.add(hub.pk)

        # --- 2. Primary service ---
        primary_service = getattr(page, "primary_service", None)
        if primary_service and primary_service.pk not in seen_ids:
            if primary_service.live:
                suggestions.append({
                    "page_id": primary_service.pk,
                    "title": primary_service.title,
                    "url": primary_service.url,
                    "reason": "Primary service (conversion destination)",
                    "score": 1.0,
                })
                seen_ids.add(primary_service.pk)

        # --- 3. Same-pillar spokes ---
        if pillar:
            spokes = (
                BlogPostPage.objects.live()
                .filter(pillar=pillar)
                .exclude(pk__in=seen_ids)
                .order_by("-first_published_at")[:5]
            )
            for spoke in spokes:
                suggestions.append({
                    "page_id": spoke.pk,
                    "title": spoke.title,
                    "url": spoke.url,
                    "reason": f"Same pillar: {pillar.name}",
                    "score": 0.8,
                })
                seen_ids.add(spoke.pk)

        # --- 4. Embedding similarity ---
        try:
            similar = cls._find_similar_by_embedding(page, seen_ids, limit=5)
            for item in similar:
                suggestions.append(item)
                seen_ids.add(item["page_id"])
        except Exception:
            pass

        # --- 5. Same category ---
        category = getattr(page, "category", None)
        if category:
            same_cat = (
                BlogPostPage.objects.live()
                .filter(category=category)
                .exclude(pk__in=seen_ids)
                .order_by("-first_published_at")[:3]
            )
            for post in same_cat:
                suggestions.append({
                    "page_id": post.pk,
                    "title": post.title,
                    "url": post.url,
                    "reason": f"Same category: {category.name}",
                    "score": 0.5,
                })
                seen_ids.add(post.pk)

        # Deduplicate and rank
        suggestions.sort(key=lambda x: -x["score"])
        return suggestions[:max_suggestions]

    # ------------------------------------------------------------------
    # 2. VALIDATE — called by pre-publish hook
    # ------------------------------------------------------------------

    @classmethod
    def validate_linking_health(cls, page) -> dict:
        """
        Check a page's linking health.

        Returns:
            {
                "internal_link_count": int,
                "has_service_route": bool,
                "has_pillar_hub_link": bool,
                "warnings": [str, ...],
            }
        """
        warnings = []
        body = getattr(page, "body", None)

        # Count internal link blocks
        internal_link_count = 0
        if body:
            for block in body:
                if block.block_type in ("internal_link", "related_posts"):
                    internal_link_count += 1

        if internal_link_count < 2:
            warnings.append(
                f"Only {internal_link_count} internal link(s) — "
                f"consider adding more for SEO and user navigation"
            )

        # Service route check
        has_service = bool(getattr(page, "primary_service", None))
        if not has_service and hasattr(page, "primary_service"):
            warnings.append(
                "No primary service linked — this post doesn't "
                "contribute to any conversion funnel"
            )

        # Pillar hub check
        pillar = getattr(page, "pillar", None)
        has_hub_link = False
        if pillar and pillar.hub_post:
            if body:
                for block in body:
                    if block.block_type == "internal_link":
                        value = block.value
                        if isinstance(value, dict):
                            linked = value.get("page")
                            if linked and linked.pk == pillar.hub_post.pk:
                                has_hub_link = True
                                break

            if not has_hub_link:
                warnings.append(
                    f"No link to pillar hub '{pillar.hub_post.title}' — "
                    f"consider adding one to reinforce topical authority"
                )

        return {
            "internal_link_count": internal_link_count,
            "has_service_route": has_service,
            "has_pillar_hub_link": has_hub_link,
            "warnings": warnings,
        }

    # ------------------------------------------------------------------
    # 3. MAINTAIN — called by weekly Celery task
    # ------------------------------------------------------------------

    @classmethod
    def find_orphan_pages(cls, site) -> list[dict]:
        """
        Find published pages with ZERO inbound internal links.
        These pages are invisible to readers navigating the site.

        Returns list of {"page_id", "title", "url", "page_type"}.
        """
        from cms_blog.models import BlogPostPage
        from cms_content_graph.models import ContentRelationship

        orphans = []

        all_live_posts = (
            BlogPostPage.objects.live()
            .descendant_of(site.root_page, inclusive=False)
        )

        # Pages that ARE linked to by at least one relationship
        linked_to_ids = set(
            ContentRelationship.objects.values_list("to_post_id", flat=True)
        )

        for post in all_live_posts:
            if post.pk not in linked_to_ids:
                orphans.append({
                    "page_id": post.pk,
                    "title": post.title,
                    "url": post.url,
                    "page_type": "BlogPostPage",
                })

        return orphans

    @classmethod
    def find_dead_end_pages(cls, site) -> list[dict]:
        """
        Find published pages with ZERO outbound internal links.
        These pages don't pass authority or guide readers onward.
        """
        from cms_blog.models import BlogPostPage

        dead_ends = []

        all_live_posts = (
            BlogPostPage.objects.live()
            .descendant_of(site.root_page, inclusive=False)
        )

        for post in all_live_posts:
            body = getattr(post, "body", None)
            if not body:
                dead_ends.append({
                    "page_id": post.pk,
                    "title": post.title,
                    "url": post.url,
                })
                continue

            has_outbound = any(
                block.block_type in ("internal_link", "related_posts", "cta")
                for block in body
            )
            if not has_outbound:
                dead_ends.append({
                    "page_id": post.pk,
                    "title": post.title,
                    "url": post.url,
                })

        return dead_ends

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def _find_similar_by_embedding(
        cls, page, exclude_ids: set, limit: int = 5
    ) -> list[dict]:
        """Find similar pages via vector embedding cosine similarity."""
        from django.contrib.contenttypes.models import ContentType

        from cms_intelligence.models import ContentEmbedding

        ct = ContentType.objects.get_for_model(page)

        try:
            source_embedding = ContentEmbedding.objects.get(
                content_type=ct, object_id=page.pk
            )
        except ContentEmbedding.DoesNotExist:
            return []

        source_vec = source_embedding.embedding
        if not source_vec:
            return []

        # Get all other embeddings for the same content type on this site
        other_embeddings = (
            ContentEmbedding.objects.filter(content_type=ct)
            .exclude(object_id__in=exclude_ids)
        )

        # Compute cosine similarity in Python (for small datasets)
        # For large datasets, use pgvector or a vector DB
        import math

        def cosine_sim(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return dot / (norm_a * norm_b)

        scored = []
        for emb in other_embeddings:
            if not emb.embedding:
                continue
            sim = cosine_sim(source_vec, emb.embedding)
            if sim > 0.6:  # threshold
                scored.append((emb.object_id, sim))

        scored.sort(key=lambda x: -x[1])

        results = []
        from wagtail.models import Page

        for obj_id, sim in scored[:limit]:
            try:
                target_page = Page.objects.get(pk=obj_id).specific
                if target_page.live:
                    results.append({
                        "page_id": target_page.pk,
                        "title": target_page.title,
                        "url": target_page.url,
                        "reason": f"Topically similar ({sim:.0%})",
                        "score": round(sim, 2),
                    })
            except Page.DoesNotExist:
                pass

        return results
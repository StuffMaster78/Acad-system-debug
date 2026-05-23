"""
Content Embedding Generation
===============================

Generate vector embeddings for content pages using OpenAI's
text-embedding-3-small (or configurable alternative).

Used by cms_content_graph's InternalLinkingService for
similarity-based link suggestions.

Triggered on publish (via Wagtail hook) and by a weekly
full-reindex task.

Configuration::

    OPENAI_API_KEY = "sk-..."
    EMBEDDING_MODEL = "text-embedding-3-small"  # default
    EMBEDDING_ENABLED = True  # False to skip in dev
"""

import hashlib
import logging

from celery import shared_task
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = getattr(settings, "EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_ENABLED = getattr(settings, "EMBEDDING_ENABLED", False)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def generate_embedding_for_page(self, page_id: int):
    """Generate an embedding for a single page. Called on publish."""
    if not EMBEDDING_ENABLED:
        return {"skipped": True, "reason": "EMBEDDING_ENABLED is False"}

    from wagtail.models import Page

    from cms_intelligence.models import ContentEmbedding

    try:
        page = Page.objects.get(pk=page_id).specific
    except Page.DoesNotExist:
        return {"error": "Page not found"}

    # Extract text from the page
    text = _extract_text(page)
    if not text or len(text.strip()) < 50:
        return {"skipped": True, "reason": "Insufficient text content"}

    # Check if embedding is already current
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    ct = ContentType.objects.get_for_model(page)

    existing = ContentEmbedding.objects.filter(
        content_type=ct, object_id=page.pk,
    ).first()

    if existing and existing.source_text_hash == text_hash:
        return {"skipped": True, "reason": "Embedding already current"}

    # Generate embedding
    try:
        vector = _call_embedding_api(text)
    except Exception as exc:
        logger.error("Embedding generation failed for page %s: %s", page_id, exc)
        raise self.retry(exc=exc)

    # Store
    ContentEmbedding.objects.update_or_create(
        content_type=ct,
        object_id=page.pk,
        defaults={
            "embedding": vector,
            "model_name": EMBEDDING_MODEL,
            "source_text_hash": text_hash,
        },
    )

    logger.info("Embedding generated for page %s (%s)", page_id, page.title[:50])
    return {"page_id": page_id, "dimensions": len(vector)}


@shared_task
def reindex_all_embeddings():
    """Weekly task: regenerate embeddings for all published pages."""
    from wagtail.models import Page, Site

    if not EMBEDDING_ENABLED:
        return {"skipped": True, "reason": "EMBEDDING_ENABLED is False"}

    count = 0
    for site in Site.objects.all():
        pages = Page.objects.live().descendant_of(site.root_page, inclusive=False)
        for page in pages.iterator(chunk_size=100):
            generate_embedding_for_page.delay(page.pk)
            count += 1

    logger.info("Queued %d pages for embedding generation", count)
    return {"pages_queued": count}


def _extract_text(page) -> str:
    """Extract plain text from a page's title + body for embedding."""
    parts = [page.title]

    # Excerpt
    excerpt = getattr(page, "excerpt", "")
    if excerpt:
        parts.append(excerpt)

    # StreamField body
    body = getattr(page, "body", None)
    if body:
        for block in body:
            if block.block_type == "paragraph":
                parts.append(strip_tags(str(block.value)))
            elif block.block_type == "heading":
                value = block.value
                if isinstance(value, dict):
                    parts.append(value.get("text", ""))
            elif block.block_type in ("callout", "quote"):
                value = block.value
                if isinstance(value, dict):
                    parts.append(strip_tags(str(value.get("text", ""))))
            elif block.block_type == "faq":
                value = block.value
                if isinstance(value, dict):
                    parts.append(value.get("question", ""))
                    parts.append(strip_tags(str(value.get("answer", ""))))
            elif block.block_type == "list":
                value = block.value
                if isinstance(value, dict):
                    items = value.get("items", [])
                    for item in items:
                        parts.append(strip_tags(str(item)))

    text = " ".join(parts)

    # Truncate to ~8000 tokens (~32000 chars) for API limits
    if len(text) > 32000:
        text = text[:32000]

    return text


def _call_embedding_api(text: str) -> list[float]:
    """Call OpenAI's embedding API. Returns a list of floats."""
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured in settings")

    import requests

    response = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "input": text,
            "model": EMBEDDING_MODEL,
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenAI embedding API error: {response.status_code} — {response.text[:200]}"
        )

    data = response.json()
    return data["data"][0]["embedding"]

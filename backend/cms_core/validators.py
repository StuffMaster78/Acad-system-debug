"""
Pre-Publish Validation Framework
=================================

Three tiers:
- Blockers: prevent publishing until fixed
- Warnings: allow publish but flag the issue
- Suggestions: informational, no impact on publish

Validators are registered via Wagtail hooks in wagtail_hooks.py.
"""

import re
from django.utils.html import strip_tags
from wagtail.blocks import StreamValue


class ValidationResult:
    """Container for validation output."""

    def __init__(self):
        self.blockers = []
        self.warnings = []
        self.suggestions = []

    @property
    def is_publishable(self):
        return len(self.blockers) == 0

    def add_blocker(self, message, field=None):
        self.blockers.append({"message": message, "field": field})

    def add_warning(self, message, field=None):
        self.warnings.append({"message": message, "field": field})

    def add_suggestion(self, message, field=None):
        self.suggestions.append({"message": message, "field": field})

    def to_dict(self):
        return {
            "is_publishable": self.is_publishable,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
        }


def validate_page_for_publish(page):
    """Run all validators against a page. Returns ValidationResult."""
    result = ValidationResult()

    # --- BLOCKERS ---

    # Meta title length
    seo_title = getattr(page, "seo_title", "") or ""
    if seo_title and len(seo_title) > 60:
        result.add_blocker(
            f"Meta title too long: {len(seo_title)}/60 characters",
            field="seo_title",
        )

    # Meta description length
    search_desc = getattr(page, "search_description", "") or ""
    if search_desc and len(search_desc) > 160:
        result.add_blocker(
            f"Meta description too long: {len(search_desc)}/160 characters",
            field="search_description",
        )

    # Body exists and is not empty
    body = getattr(page, "body", None)
    if body is not None:
        if isinstance(body, StreamValue) and len(body) == 0:
            result.add_blocker(
                "Page body is empty — add content before publishing",
                field="body",
            )

        # Image alt text check
        _validate_image_alt_texts(body, result)

        # Heading hierarchy check
        _validate_heading_hierarchy(body, result)

    # --- WARNINGS ---

    # Meta title missing
    if not seo_title:
        result.add_warning(
            "No meta title set — will use page title as fallback",
            field="seo_title",
        )

    # Meta description missing
    if not search_desc:
        result.add_warning(
            "No meta description set — consider adding one for better SERP appearance",
            field="search_description",
        )

    # Word count guidance (never a blocker per Google's guidelines)
    if body is not None:
        word_count = _count_words_in_streamfield(body)
        page_type = page.__class__.__name__

        if page_type == "BlogPostPage" and word_count < 1000:
            result.add_warning(
                f"Blog post is {word_count} words — consider expanding "
                f"for stronger topical coverage",
            )
        elif page_type == "ServicePage" and word_count < 800:
            result.add_warning(
                f"Service page is {word_count} words — consider adding more "
                f"detail to support conversion",
            )

    # Blog-specific: author check
    primary_author = getattr(page, "primary_author", None)
    if hasattr(page, "primary_author") and not primary_author:
        result.add_blocker(
            "Primary author is required for blog posts",
            field="primary_author",
        )

    # Blog-specific: service route check
    primary_service = getattr(page, "primary_service", None)
    if hasattr(page, "primary_service") and not primary_service:
        result.add_warning(
            "No primary service page linked — this post won't route "
            "readers toward a conversion destination",
            field="primary_service",
        )

    # Blog-specific: excerpt check
    excerpt = getattr(page, "excerpt", None)
    if hasattr(page, "excerpt") and not excerpt:
        result.add_warning(
            "No excerpt set — used for listings and social sharing",
            field="excerpt",
        )

    # Service-specific: CTA check
    if hasattr(page, "primary_cta_text") and body is not None:
        has_cta = any(
            block.block_type in ("cta", "hero")
            for block in body
        )
        if not has_cta:
            result.add_warning(
                "Service page has no CTA or Hero block — "
                "consider adding one for conversion",
            )

    # --- SUGGESTIONS ---

    # Internal links count
    if body is not None:
        internal_link_count = sum(
            1 for block in body
            if block.block_type == "internal_link"
        )
        if internal_link_count < 3:
            result.add_suggestion(
                f"Only {internal_link_count} internal link(s) — "
                f"consider adding more for SEO and reader navigation",
            )

    # FAQ count for schema eligibility
    if body is not None:
        faq_count = sum(
            1 for block in body if block.block_type == "faq"
        )
        if 0 < faq_count < 3:
            result.add_suggestion(
                f"Only {faq_count} FAQ item(s) — add {3 - faq_count} more "
                f"to qualify for FAQPage schema markup",
            )

    return result


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def _count_words_in_streamfield(body):
    """Count words across all text-bearing blocks in a StreamField."""
    total = 0
    for block in body:
        if block.block_type == "paragraph":
            text = strip_tags(str(block.value))
            total += len(text.split())
        elif block.block_type == "heading":
            value = block.value
            if isinstance(value, dict):
                total += len(value.get("text", "").split())
        elif block.block_type in ("callout", "quote"):
            value = block.value
            if isinstance(value, dict):
                text = strip_tags(str(value.get("text", "")))
                total += len(text.split())
        elif block.block_type == "faq":
            value = block.value
            if isinstance(value, dict):
                total += len(value.get("question", "").split())
                total += len(strip_tags(str(value.get("answer", ""))).split())
    return total


def _validate_image_alt_texts(body, result):
    """Check all image blocks have alt text."""
    for block in body:
        if block.block_type == "image":
            value = block.value
            if isinstance(value, dict):
                alt = value.get("alt_text", "")
                if not alt or not alt.strip():
                    result.add_blocker(
                        "An image block is missing alt text — "
                        "required for accessibility and SEO",
                        field="body",
                    )
                    return # One error is enough


def _validate_heading_hierarchy(body, result):
    """Check heading levels don't skip (H2 → H4 without H3)."""
    last_level = 1 # H1 is the page title
    for block in body:
        if block.block_type == "heading":
            value = block.value
            if isinstance(value, dict):
                level_str = value.get("level", "h2")
                level = int(level_str.replace("h", ""))
                if level > last_level + 1:
                    result.add_blocker(
                        f"Heading hierarchy skips from H{last_level} to H{level} — "
                        f"add an H{last_level + 1} in between",
                        field="body",
                    )
                    return
                last_level = level


def get_reading_time(word_count, wpm=250):
    """Estimated reading time from word count."""
    minutes = word_count / wpm
    if minutes < 1:
        return "Under 1 min read"
    elif minutes < 2:
        return "1 min read"
    else:
        return f"{int(minutes)} min read"


def generate_toc(body):
    """Generate table of contents from heading blocks.
    Returns a list of dicts: [{level, text, anchor_id}, ...]"""
    toc = []
    for block in body:
        if block.block_type == "heading":
            value = block.value
            if isinstance(value, dict):
                text = value.get("text", "")
                level = value.get("level", "h2")
                anchor_id = re.sub(
                    r"[^a-z0-9-]", "",
                    text.lower().replace(" ", "-")
                )[:60]
                toc.append({
                    "level": level,
                    "text": text,
                    "anchor_id": anchor_id,
                })
    return toc
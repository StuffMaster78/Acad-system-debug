"""
Content Importer Service
==========================

Converts pasted HTML (from Google Docs, Word, or web pages) into
a list of StreamField block dicts.

The editor pastes their content into a "Paste from Document" dialog.
The importer:
1. Cleans the HTML (strips Office cruft, inline styles)
2. Splits into blocks based on HTML structure (headings, paragraphs,
   lists, images, blockquotes, tables, code blocks)
3. Returns a list of StreamField-compatible block dicts
4. The frontend inserts these blocks into the page's StreamField

This is NOT a WYSIWYG pasting directly into Draftail — it's a
separate import step that produces structured blocks from unstructured
paste content.

Usage:
    from cms_core.services.content_importer import ContentImporter

    blocks = ContentImporter.html_to_blocks(pasted_html)
    # Returns: [
    # {"type": "heading", "value": {"text": "Introduction", "level": "h2"}},
    # {"type": "paragraph", "value": "<p>The first paragraph...</p>"},
    # {"type": "list", "value": {"style": "bulleted", "items": [...]}},
    # ...
    # ]
"""

from __future__ import annotations

import logging
import re
from typing import Any

from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# Tags that indicate block boundaries (content before/after these
# should be in separate blocks)
BLOCK_BOUNDARY_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "div",
    "ul", "ol",
    "blockquote",
    "table",
    "pre",
    "hr",
    "figure", "img",
}

# Microsoft Office junk patterns
OFFICE_CRUFT_PATTERNS = [
    re.compile(r"<o:p>.*?</o:p>", re.DOTALL),
    re.compile(r"<\?xml.*?\?>", re.DOTALL),
    re.compile(r"<!--\[if.*?endif\]-->", re.DOTALL),
    re.compile(r"<!--.*?-->", re.DOTALL),
    re.compile(r'class="Mso\w+"'),
    re.compile(r'style="[^"]*mso-[^"]*"'),
    re.compile(r"<w:.*?</w:.*?>", re.DOTALL),
    re.compile(r"<m:.*?</m:.*?>", re.DOTALL),
    re.compile(r"</?font[^>]*>"),
    re.compile(r"</?span[^>]*>"), # Remove all spans (styling carriers)
]

# Inline style patterns to strip
STYLE_STRIP = re.compile(r'\s*style="[^"]*"')
CLASS_STRIP = re.compile(r'\s*class="[^"]*"')
ID_STRIP = re.compile(r'\s*id="[^"]*"')
DATA_STRIP = re.compile(r'\s*data-[a-z-]+="[^"]*"')


class ContentImporter:
    """Convert pasted HTML into StreamField blocks."""

    @classmethod
    def html_to_blocks(cls, html: str) -> list[dict[str, Any]]:
        """
        Main entry point. Accepts raw HTML (from paste), returns
        a list of StreamField block dicts.

        The returned blocks are ready to be inserted into a
        BlogPostPage.body or ServicePage.body StreamField.
        """
        if not html or not html.strip():
            return []

        # Step 1: Clean HTML
        cleaned = cls._clean_html(html)

        # Step 2: Parse into block-level elements
        blocks = cls._split_into_blocks(cleaned)

        # Step 3: Convert each element to a StreamField block dict
        streamfield_blocks = []
        for block in blocks:
            converted = cls._element_to_block(block)
            if converted:
                streamfield_blocks.append(converted)

        # Step 4: Post-process (merge adjacent same-type blocks, etc.)
        streamfield_blocks = cls._post_process(streamfield_blocks)

        logger.info(
            "Imported %d blocks from %d characters of HTML",
            len(streamfield_blocks),
            len(html),
        )
        return streamfield_blocks

    @classmethod
    def plain_text_to_blocks(cls, text: str) -> list[dict[str, Any]]:
        """
        Convert plain text to blocks.
        Splits on double newlines (paragraph breaks).
        Lines starting with # are treated as headings.
        Lines starting with - or * are treated as list items.
        """
        if not text or not text.strip():
            return []

        blocks = []
        current_list_items = []
        current_list_style = None

        for line in text.split("\n"):
            stripped = line.strip()

            if not stripped:
                # Flush any pending list
                if current_list_items:
                    blocks.append({
                        "type": "list",
                        "value": {
                            "style": current_list_style or "bulleted",
                            "items": current_list_items,
                        },
                    })
                    current_list_items = []
                    current_list_style = None
                continue

            # Headings (markdown-style)
            if stripped.startswith("### "):
                blocks.append({
                    "type": "heading",
                    "value": {"text": stripped[4:], "level": "h4"},
                })
            elif stripped.startswith("## "):
                blocks.append({
                    "type": "heading",
                    "value": {"text": stripped[3:], "level": "h3"},
                })
            elif stripped.startswith("# "):
                blocks.append({
                    "type": "heading",
                    "value": {"text": stripped[2:], "level": "h2"},
                })

            # List items
            elif stripped.startswith(("- ", "* ", "• ")):
                current_list_style = "bulleted"
                current_list_items.append(f"<p>{stripped[2:]}</p>")
            elif re.match(r"^\d+[\.\)]\s", stripped):
                current_list_style = "numbered"
                item_text = re.sub(r"^\d+[\.\)]\s", "", stripped)
                current_list_items.append(f"<p>{item_text}</p>")

            # Horizontal rule
            elif stripped in ("---", "***", "___"):
                blocks.append({"type": "divider", "value": {}})

            # Regular paragraph
            else:
                # Flush pending list first
                if current_list_items:
                    blocks.append({
                        "type": "list",
                        "value": {
                            "style": current_list_style or "bulleted",
                            "items": current_list_items,
                        },
                    })
                    current_list_items = []
                    current_list_style = None

                blocks.append({
                    "type": "paragraph",
                    "value": f"<p>{stripped}</p>",
                })

        # Flush final list
        if current_list_items:
            blocks.append({
                "type": "list",
                "value": {
                    "style": current_list_style or "bulleted",
                    "items": current_list_items,
                },
            })

        return blocks

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    @classmethod
    def _clean_html(cls, html: str) -> str:
        """Strip Office cruft, inline styles, and normalize whitespace."""

        # Remove Office namespace junk
        for pattern in OFFICE_CRUFT_PATTERNS:
            html = pattern.sub("", html)

        # Strip style, class, id, data attributes
        html = STYLE_STRIP.sub("", html)
        html = CLASS_STRIP.sub("", html)
        html = ID_STRIP.sub("", html)
        html = DATA_STRIP.sub("", html)

        # Remove empty tags
        html = re.sub(r"<(\w+)>\s*</\1>", "", html)

        # Normalize whitespace between tags
        html = re.sub(r">\s+<", ">\n<", html)

        # Remove leading/trailing whitespace
        html = html.strip()

        return html

    @classmethod
    def _split_into_blocks(cls, html: str) -> list[dict]:
        """
        Parse cleaned HTML into a list of block-level elements.
        Each element is a dict: {"tag": "h2", "html": "<h2>Title</h2>"}

        Uses a simple regex-based splitter rather than a full DOM parser.
        For production, consider using BeautifulSoup for robustness.
        """
        try:
            from bs4 import BeautifulSoup

            return cls._split_with_beautifulsoup(html)
        except ImportError:
            return cls._split_with_regex(html)

    @classmethod
    def _split_with_beautifulsoup(cls, html: str) -> list[dict]:
        """Split using BeautifulSoup (preferred, more robust)."""
        from bs4 import BeautifulSoup, NavigableString

        soup = BeautifulSoup(html, "html.parser")

        # Find the body or use the whole soup
        body = soup.find("body") or soup

        blocks = []
        for element in body.children:
            if isinstance(element, NavigableString):
                text = element.strip()
                if text:
                    blocks.append({"tag": "p", "html": f"<p>{text}</p>"})
                continue

            tag = element.name
            if tag in BLOCK_BOUNDARY_TAGS:
                blocks.append({"tag": tag, "html": str(element)})
            elif tag in ("strong", "em", "a", "b", "i"):
                # Inline element at top level — wrap in paragraph
                blocks.append({"tag": "p", "html": f"<p>{element}</p>"})

        return blocks

    @classmethod
    def _split_with_regex(cls, html: str) -> list[dict]:
        """Fallback regex splitter when BeautifulSoup isn't available."""
        blocks = []
        # Split on block-level tags
        pattern = re.compile(
            r"(<(?:h[1-6]|p|div|ul|ol|blockquote|table|pre|hr|figure)[^>]*>.*?</(?:h[1-6]|p|div|ul|ol|blockquote|table|pre|figure)>|<hr\s*/?>)",
            re.DOTALL | re.IGNORECASE,
        )
        matches = pattern.findall(html)
        for match in matches:
            tag_match = re.match(r"<(\w+)", match)
            tag = tag_match.group(1).lower() if tag_match else "p"
            blocks.append({"tag": tag, "html": match})

        return blocks

    @classmethod
    def _element_to_block(cls, element: dict) -> dict | None:
        """Convert a parsed HTML element to a StreamField block dict."""
        tag = element["tag"]
        html = element["html"]

        # --- Headings ---
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            text = strip_tags(html).strip()
            if not text:
                return None
            # Map h1 to h2 (page title is the only h1)
            level = tag if tag != "h1" else "h2"
            # Cap at h4 (our block only supports h2-h4)
            if level in ("h5", "h6"):
                level = "h4"
            return {
                "type": "heading",
                "value": {"text": text, "level": level},
            }

        # --- Paragraphs ---
        if tag in ("p", "div"):
            # Clean the paragraph HTML — keep only allowed inline tags
            cleaned = cls._clean_inline_html(html)
            if not strip_tags(cleaned).strip():
                return None
            # Ensure wrapped in <p>
            if not cleaned.strip().startswith("<p"):
                cleaned = f"<p>{cleaned}</p>"
            return {
                "type": "paragraph",
                "value": cleaned,
            }

        # --- Lists ---
        if tag in ("ul", "ol"):
            items = re.findall(r"<li[^>]*>(.*?)</li>", html, re.DOTALL)
            if not items:
                return None
            clean_items = []
            for item in items:
                clean = cls._clean_inline_html(item).strip()
                if clean:
                    if not clean.startswith("<p"):
                        clean = f"<p>{clean}</p>"
                    clean_items.append(clean)
            if not clean_items:
                return None
            return {
                "type": "list",
                "value": {
                    "style": "numbered" if tag == "ol" else "bulleted",
                    "items": clean_items,
                },
            }

        # --- Blockquotes ---
        if tag == "blockquote":
            text = cls._clean_inline_html(html)
            text = re.sub(r"</?blockquote[^>]*>", "", text).strip()
            if not strip_tags(text).strip():
                return None
            return {
                "type": "quote",
                "value": {"text": text, "attribution": ""},
            }

        # --- Code blocks ---
        if tag == "pre":
            code = strip_tags(html).strip()
            if not code:
                return None
            return {
                "type": "code",
                "value": {"language": "text", "code": code, "caption": ""},
            }

        # --- Horizontal rules ---
        if tag == "hr":
            return {"type": "divider", "value": {}}

        # --- Tables ---
        if tag == "table":
            # Tables become paragraphs with the raw HTML preserved
            # (our block library doesn't have a generic table block for blogs)
            return {
                "type": "paragraph",
                "value": f"<p>{strip_tags(html).strip()}</p>",
            }

        # --- Images ---
        if tag in ("figure", "img"):
            # Images from paste can't be uploaded automatically —
            # flag them as a paragraph with a note
            alt = ""
            alt_match = re.search(r'alt="([^"]*)"', html)
            if alt_match:
                alt = alt_match.group(1)
            return {
                "type": "paragraph",
                "value": f"<p><em>[Image: {alt or 'paste image here manually'}]</em></p>",
            }

        return None

    @classmethod
    def _clean_inline_html(cls, html: str) -> str:
        """
        Clean inline HTML within a block.
        Keep only: <strong>, <em>, <a>, <b>, <i>, <br>
        Strip everything else.
        """
        # Remove all tags except allowed ones
        allowed = {"strong", "em", "a", "b", "i", "br", "p", "sup", "sub"}

        def replace_tag(match):
            full_tag = match.group(0)
            tag_name = match.group(1).lower().strip("/")
            if tag_name in allowed:
                # For <a> tags, keep href only
                if tag_name == "a":
                    href_match = re.search(r'href="([^"]*)"', full_tag)
                    if href_match and full_tag.startswith("<a"):
                        return f'<a href="{href_match.group(1)}">'
                    elif full_tag.startswith("</"):
                        return "</a>"
                    return ""
                return full_tag
            return ""

        cleaned = re.sub(r"<(/?\w+)[^>]*>", replace_tag, html)

        # Normalize <b> to <strong>, <i> to <em>
        cleaned = cleaned.replace("<b>", "<strong>").replace("</b>", "</strong>")
        cleaned = cleaned.replace("<i>", "<em>").replace("</i>", "</em>")

        return cleaned

    @classmethod
    def _post_process(cls, blocks: list[dict]) -> list[dict]:
        """
        Post-process block list:
        - Remove empty blocks
        - Merge adjacent paragraphs that are very short (likely a split artifact)
        """
        if not blocks:
            return []

        result = []
        for block in blocks:
            if block["type"] == "paragraph":
                text = strip_tags(str(block["value"])).strip()
                if not text:
                    continue
            result.append(block)

        return result
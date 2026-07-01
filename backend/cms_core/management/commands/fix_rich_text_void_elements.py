"""
Scan all CMS page types with RichTextField or StreamField bodies and fix
HTML void elements that would crash Wagtail's admin editor.

Root cause:
  Wagtail's HtmlToContentStateHandler (Draftail converter) pushes EVERY
  opening tag onto an element stack.  HTML void elements (<img>, <input>,
  <source>, etc.) have no closing tag, so they are never popped — the next
  closing tag sees a mismatched top-of-stack and raises:

      AssertionError: Unmatched tags: expected img, got p

  Two patterns are fixed:
  1. Bare void elements   <img src="...">   → self-closing <img src="..."/>
     Python's HTMLParser calls handle_startendtag() for self-closing tags,
     which pushes and immediately pops the element, keeping the stack balanced.

  2. <br> inside <p>      <p><br></p>       → <p>&nbsp;</p>
     Wagtail registers a LineBreakHandler for <br>, but the element is still
     pushed to open_elements.  When </p> arrives the stack top is br, not p.

Run after any bulk content import from TinyMCE/WordPress/external CMS:
    python manage.py fix_rich_text_void_elements
    python manage.py fix_rich_text_void_elements --dry-run   # preview only
    python manage.py fix_rich_text_void_elements --verify    # parse test only
"""
from __future__ import annotations

import json
import re

from django.core.management.base import BaseCommand
from django.db import connection

_HTML_VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

_SKIP_VOID = {"br", "hr"}   # already handled by Wagtail — only need self-close treatment


def _make_void_self_closing(html: str) -> str:
    """
    Convert bare void elements  <tag attr>  →  <tag attr/>
    so Python's HTMLParser calls handle_startendtag (balanced push+pop).
    Skips <br> and <hr> which Wagtail's converter already handles.
    """
    def _replace(m: re.Match) -> str:
        tag = m.group(1).lower()
        if tag in _HTML_VOID_ELEMENTS and tag not in _SKIP_VOID:
            raw = m.group(0)
            if not raw.rstrip().endswith("/>"):
                return raw.rstrip().rstrip(">").rstrip() + "/>"
        return m.group(0)

    return re.sub(r"<([a-zA-Z][a-zA-Z0-9]*)([^>]*)>", _replace, html)


def _fix_br_in_p(html: str) -> str:
    """Remove <br> (and TinyMCE bogus <br data-mce-bogus="1">) from inside <p>."""
    # Empty spacer paragraph <p><br></p> → <p>&nbsp;</p>
    fixed = re.sub(r"<p>\s*<br[^>]*>\s*</p>", "<p>&nbsp;</p>", html)
    # Leading <br> at start of <p>
    fixed = re.sub(r"(<p[^>]*>)\s*<br[^>]*/?>", r"\1", fixed)
    # Any remaining bare <br> (including with attributes)
    fixed = re.sub(r"<br[^>]*>", " ", fixed)
    return fixed


def _fix_html(html: str) -> tuple[str, bool]:
    if not html:
        return html, False
    out = _fix_br_in_p(html)
    out = _make_void_self_closing(out)
    return out, out != html


def _iter_html_blocks(body_json: str | list) -> list[dict]:
    """Return list of (index, block) tuples for all blocks with string values."""
    blocks = json.loads(body_json) if isinstance(body_json, str) else body_json
    if not isinstance(blocks, list):
        return []
    return list(enumerate(blocks))


def _fix_streamfield(raw: str | list) -> tuple[str, bool]:
    body_str = raw if isinstance(raw, str) else json.dumps(raw)
    # Quick pre-check
    if not any(f"<{el}" in body_str.lower() for el in _HTML_VOID_ELEMENTS):
        return body_str, False

    blocks = json.loads(body_str)
    changed = False

    for b in blocks if isinstance(blocks, list) else []:
        val = b.get("value", "")
        if isinstance(val, str):
            new_val, c = _fix_html(val)
            if c:
                b["value"] = new_val
                changed = True
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    v = item.get("value", "")
                    if isinstance(v, str):
                        new_v, c = _fix_html(v)
                        if c:
                            item["value"] = new_v
                            changed = True

    return json.dumps(blocks) if changed else body_str, changed


def _fix_rich_text(raw: str) -> tuple[str, bool]:
    return _fix_html(str(raw) if raw else "")


def _parse_test(html: str) -> tuple[bool, str]:
    from wagtail.admin.rich_text.converters.html_to_contentstate import (
        HtmlToContentStateHandler,
    )
    handler = HtmlToContentStateHandler(["bold", "italic", "link", "ol", "ul", "h2", "h3"])
    try:
        handler.feed(html)
        return True, ""
    except AssertionError as e:
        return False, str(e)


_TARGETS: list[tuple[str, str, list[str], str]] = [
    # (table, pk_col, [fields], kind)
    ("cms_blog_blogpostpage",              "page_ptr_id", ["body"],                           "stream"),
    ("cms_service_pages_servicepage",      "page_ptr_id", ["body", "includes_items", "delivers_items"], "stream"),
    ("cms_guides_guidearticlepage",        "page_ptr_id", ["body"],                           "rich"),
    ("cms_core_tenanthomepage",            "page_ptr_id", ["intro", "home_seo_body"],         "mixed"),
    ("cms_blog_blogindexpage",             "page_ptr_id", ["intro"],                          "rich"),
    ("cms_service_pages_serviceindexpage", "page_ptr_id", ["intro"],                          "rich"),
    ("cms_core_authorindexpage",           "page_ptr_id", ["intro"],                          "rich"),
    ("cms_core_resourceindexpage",         "page_ptr_id", ["intro"],                          "rich"),
]

# intro = rich, home_seo_body = stream
_MIXED_KINDS = {
    "cms_core_tenanthomepage": {
        "intro": "rich",
        "home_seo_body": "stream",
    },
}


class Command(BaseCommand):
    help = (
        "Fix HTML void elements in all CMS rich text / StreamField bodies "
        "that would crash the Wagtail Draftail editor."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without writing anything.",
        )
        parser.add_argument(
            "--verify",
            action="store_true",
            help="Run the Draftail parse test only (no changes). Exits non-zero if failures.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verify = options["verify"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be written.\n"))

        total_scanned = total_fixed = total_failures = 0

        for table, pk_col, fields, default_kind in _TARGETS:
            mixed = _MIXED_KINDS.get(table, {})
            for field in fields:
                kind = mixed.get(field, default_kind)
                try:
                    with connection.cursor() as cur:
                        cur.execute(
                            f"SELECT {pk_col}, {field} FROM {table} WHERE {field} IS NOT NULL"
                        )
                        rows = cur.fetchall()
                except Exception as exc:
                    self.stderr.write(f"SKIP {table}.{field}: {exc}")
                    continue

                fixed = failures = 0

                for pk, raw in rows:
                    total_scanned += 1

                    if verify:
                        html_vals = (
                            [str(raw)] if kind == "rich"
                            else [
                                b.get("value", "")
                                for b in (
                                    json.loads(raw) if isinstance(raw, str) else raw
                                    if isinstance(raw, list) else []
                                )
                                if isinstance(b.get("value", ""), str)
                            ]
                        )
                        for html in html_vals:
                            ok, err = _parse_test(html)
                            if not ok:
                                failures += 1
                                total_failures += 1
                                self.stderr.write(f"  FAIL pk={pk}: {err[:80]}")
                                break
                        continue

                    # Apply fix
                    if kind == "rich":
                        new_val, changed = _fix_rich_text(raw)
                    else:
                        new_val, changed = _fix_streamfield(raw)

                    if changed:
                        if not dry_run:
                            with connection.cursor() as cur:
                                cur.execute(
                                    f"UPDATE {table} SET {field} = %s WHERE {pk_col} = %s",
                                    [new_val, pk],
                                )
                        fixed += 1
                        total_fixed += 1

                tag = "verify" if verify else ("dry" if dry_run else "fixed")
                label = "failures" if verify else "changed"
                count = failures if verify else fixed
                style = self.style.ERROR if (verify and failures) else self.style.SUCCESS
                self.stdout.write(
                    style(f"  {table}.{field}: {len(rows)} pages, {count} {label}")
                )

        self.stdout.write("")
        if verify:
            if total_failures:
                self.stdout.write(self.style.ERROR(
                    f"Parse failures: {total_failures} / {total_scanned} pages"
                ))
                raise SystemExit(1)
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"All {total_scanned} pages pass the Draftail parse test."
                ))
        else:
            verb = "Would fix" if dry_run else "Fixed"
            self.stdout.write(self.style.SUCCESS(
                f"{verb} {total_fixed} / {total_scanned} pages across all CMS types."
            ))

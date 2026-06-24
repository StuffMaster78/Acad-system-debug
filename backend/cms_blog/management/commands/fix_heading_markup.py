"""
fix_heading_markup
==================
Converts bare-bold pseudo-headings to real HTML heading tags in every
BlogPostPage body.

The 740 bulk-imported posts use this pattern for section headings:
  <p><strong>Section Title</strong></p>

Real heading tags are required for:
  • The ArticleToc component (which reads h2/h3 in the HTML)
  • SEO / accessibility / screen-reader semantics
  • Proper document outline

Detection rules — a <p> is converted to <h2> when:
  1. Its entire content is a single <strong> with plain text (no nested tags)
  2. The text is ≤ 120 characters
  3. The text does not end with '.' or ',' (full sentence, not a heading)

Usage:
  python manage.py fix_heading_markup            # dry-run
  python manage.py fix_heading_markup --apply    # write to DB
  python manage.py fix_heading_markup --apply --verbose
"""

import re

from django.core.management.base import BaseCommand

# <p> whose entire content is a single <strong> with plain (no-HTML) text
_CANDIDATE_RE = re.compile(
    r'<p[^>]*>\s*<strong[^>]*>([^<]{1,120})</strong>\s*</p>',
    re.IGNORECASE,
)

_SENTENCE_ENDINGS = frozenset('.,'  )


def _is_heading(text: str) -> bool:
    t = text.strip()
    return bool(t) and t[-1] not in _SENTENCE_ENDINGS


def fix_headings(html: str) -> tuple[str, int]:
    """Return (fixed_html, number_of_conversions)."""
    count = 0

    def _replace(m: re.Match) -> str:
        nonlocal count
        text = m.group(1)
        if _is_heading(text):
            count += 1
            return f'<h2>{text}</h2>'
        return m.group(0)

    return _CANDIDATE_RE.sub(_replace, html), count


class Command(BaseCommand):
    help = "Convert <p><strong>…</strong></p> pseudo-headings to <h2> in blog bodies."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Write changes to the database (default: dry-run).",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            default=False,
            help="Print each affected page slug.",
        )

    def handle(self, *args, **options):
        apply   = options["apply"]
        verbose = options["verbose"]

        from django.db import connection  # noqa: PLC0415

        with connection.cursor() as cur:
            cur.execute(
                "SELECT p.id, p.slug, b.body "
                "FROM wagtailcore_page p "
                "JOIN cms_blog_blogpostpage b ON b.page_ptr_id = p.id"
            )
            rows = cur.fetchall()

        total       = len(rows)
        affected    = 0
        total_fixes = 0
        mode        = "APPLY" if apply else "DRY-RUN"

        self.stdout.write(f"Scanning {total} BlogPostPage objects [{mode}]…\n")

        for page_id, slug, body_json in rows:
            if not body_json:
                continue

            fixed_body, n = fix_headings(body_json)
            if not n:
                continue

            affected    += 1
            total_fixes += n

            if verbose or not apply:
                status = "FIXED" if apply else "WOULD FIX"
                self.stdout.write(
                    f"  [{status}] {slug!r:55s} ({n} heading{'s' if n != 1 else ''})"
                )

            if apply:
                with connection.cursor() as cur:
                    cur.execute(
                        "UPDATE cms_blog_blogpostpage SET body=%s WHERE page_ptr_id=%s",
                        [fixed_body, page_id],
                    )

        label = "Fixed" if apply else "Would fix"
        self.stdout.write(
            f"\n{label} {affected}/{total} pages "
            f"({total_fixes} total heading conversions).\n"
        )
        if not apply:
            self.stdout.write("Re-run with --apply to write changes.\n")

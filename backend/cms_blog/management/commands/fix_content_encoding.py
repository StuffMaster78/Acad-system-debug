"""
fix_content_encoding
=====================
Repairs mojibake in all Wagtail CMS blog content — the classic symptom of
UTF-8 text saved while the DB connection was set to Latin-1 / cp1252.

Each corrupted sequence is a 2-3 Latin-1 misread of a multi-byte UTF-8
codepoint.  For example:
  U+2019 RIGHT SINGLE QUOTATION MARK
    UTF-8:  0xE2 0x80 0x99
    Latin-1 misread: U+00E2, U+0080, U+0099  (shows as "â\\x80\\x99")

Usage:
  python manage.py fix_content_encoding            # dry-run (no DB writes)
  python manage.py fix_content_encoding --apply    # write to DB
  python manage.py fix_content_encoding --apply --verbose
"""

import json
import re

from django.core.management.base import BaseCommand

# ---------------------------------------------------------------------------
# Mojibake replacement map
# Keys: corrupted Unicode string (Latin-1 misread of UTF-8 bytes)
# Values: the correct Unicode character(s)
# ---------------------------------------------------------------------------
MOJIBAKE: dict[str, str] = {
    # Curly quotes / apostrophes (most common — Word/Google Docs paste-ins)
    "â": "’",  # right single quotation mark  '
    "â": "‘",  # left single quotation mark   '
    "â": "“",  # left double quotation mark   "
    "â": "”",  # right double quotation mark  "
    "â": "‚",  # single low-9 quotation mark  ‚
    "â": "„",  # double low-9 quotation mark  „

    # Dashes and punctuation
    "â": "–",  # en dash          –
    "â": "—",  # em dash          —
    "â¦": "…",  # horizontal ellipsis  …

    # Bullet and common symbols
    "â¢": "•",  # bullet           •
    "â¢": "™",  # trade mark sign  ™
    "Â©": "©",        # copyright sign   ©
    "Â®": "®",        # registered sign  ®
    "Â°": "°",        # degree sign      °
    "Â ": " ",             # non-breaking space → plain space

    # Accented Latin characters (common in academic citations and names)
    "Ã©": "é",  # e with acute    é
    "Ã¨": "è",  # e with grave    è
    "Ãª": "ê",  # e with circumflex  ê
    "Ã«": "ë",  # e with diaeresis   ë
    "Ã ": "à",  # a with grave    à
    "Ã¢": "â",  # a with circumflex  â
    "Ã®": "î",  # i with circumflex  î
    "Ã¯": "ï",  # i with diaeresis   ï
    "Ã´": "ô",  # o with circumflex  ô
    "Ã¹": "ù",  # u with grave    ù
    "Ã»": "û",  # u with circumflex  û
    "Ã¼": "ü",  # u with diaeresis   ü
    "Ã§": "ç",  # c with cedilla  ç
    "Ã±": "ñ",  # n with tilde    ñ
    "Ã": "Ü",  # U with diaeresis   Ü
    "Ã": "Ö",  # O with diaeresis   Ö
    "Ã": "Ä",  # A with diaeresis   Ä
}

# Build a single compiled regex for efficiency
_PATTERN = re.compile(
    "|".join(re.escape(k) for k in sorted(MOJIBAKE, key=len, reverse=True))
)


def fix(text: str) -> str:
    """Replace all known mojibake sequences in text."""
    if not text:
        return text
    return _PATTERN.sub(lambda m: MOJIBAKE[m.group(0)], text)


def fix_streamfield_json(raw_json: str) -> tuple[str, int]:
    """
    Fix mojibake inside a StreamField JSON blob.
    Returns (fixed_json, number_of_replacements).
    """
    fixed = fix(raw_json)
    # Count character-level differences as a rough replacement count
    changes = sum(1 for a, b in zip(raw_json, fixed) if a != b)
    if len(fixed) != len(raw_json):
        changes += abs(len(fixed) - len(raw_json))
    return fixed, changes


class Command(BaseCommand):
    help = "Repair mojibake (encoding corruption) in CMS blog post content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Write fixes to the database (default: dry-run only).",
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

        # Use raw SQL so we are immune to model/migration mismatches and
        # StreamField API differences across Wagtail versions.
        with connection.cursor() as cur:
            cur.execute(
                "SELECT p.id, p.slug, p.title, b.excerpt, b.body "
                "FROM wagtailcore_page p "
                "JOIN cms_blog_blogpostpage b ON b.page_ptr_id = p.id"
            )
            rows = cur.fetchall()

        total       = len(rows)
        affected    = 0
        total_fixes = 0

        mode = "APPLY" if apply else "DRY-RUN"
        self.stdout.write(f"Scanning {total} BlogPostPage objects [{mode}]…\n")

        for page_id, slug, title, excerpt, body_json in rows:
            page_dirty = False
            fixes_here = 0

            # ── Body (StreamField JSON string) ───────────────────────────────
            fixed_body, n = fix_streamfield_json(body_json or "[]")
            if n:
                page_dirty = True
                fixes_here += n

            # ── Excerpt ──────────────────────────────────────────────────────
            fixed_excerpt = fix(excerpt or "")
            if fixed_excerpt != (excerpt or ""):
                page_dirty = True
                fixes_here += 1

            # ── Title (stored in wagtailcore_page) ───────────────────────────
            fixed_title = fix(title or "")
            if fixed_title != (title or ""):
                page_dirty = True
                fixes_here += 1

            if page_dirty:
                affected    += 1
                total_fixes += fixes_here
                if verbose or not apply:
                    status = "FIXED" if apply else "WOULD FIX"
                    self.stdout.write(
                        f"  [{status}] {slug!r:55s} ({fixes_here} replacements)"
                    )
                if apply:
                    with connection.cursor() as cur:
                        cur.execute(
                            "UPDATE cms_blog_blogpostpage "
                            "SET body=%s, excerpt=%s "
                            "WHERE page_ptr_id=%s",
                            [fixed_body, fixed_excerpt, page_id],
                        )
                        cur.execute(
                            "UPDATE wagtailcore_page SET title=%s WHERE id=%s",
                            [fixed_title, page_id],
                        )

        label = "Fixed" if apply else "Would fix"
        self.stdout.write(
            f"\n{label} {affected}/{total} pages "
            f"({total_fixes} total character replacements).\n"
        )
        if not apply:
            self.stdout.write("Re-run with --apply to write changes.\n")

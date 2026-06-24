"""
fix_content_links
=================
Sweeps through all BlogPostPage and ServicePage paragraph blocks and
repairs internal href links in the stored HTML:

  1. URL-decode %XX-encoded slugs  (/foo%20bar/ → /foobar/)
  2. Strip .php extension          (/about.php  → /about)
  3. Collapse literal spaces       (/sum mary   → /summary)
  4. Fix known compound-word typos (cause-andeffect → cause-and-effect, etc.)
  5. Strip concatenated absolute URL tails
     (/foo-barhttps://example.com/foo-bar → /foo-bar)

Run with --dry-run to preview changes without saving.

Usage:
    python manage.py fix_content_links
    python manage.py fix_content_links --dry-run
"""
import re
import urllib.parse

from django.core.management.base import BaseCommand
from wagtail.models import Page


# ── Known compound-slug typos ─────────────────────────────────────────────────
# (search, replacement) — both are raw substrings inside the slug segment.
# Applied AFTER url-decoding and space-collapse so the slugs are clean first.
SLUG_TYPOS = [
    ("cause-andeffect",    "cause-and-effect"),
    ("researchtopics",     "research-topics"),
    ("essayguide",         "essay-guide"),
    ("essaywriting",       "essay-writing"),
    ("application-essay",  "application-essay"),   # no-op, but documents intent
    ("application-essay-",  "application-essay-"), # same
]


def _fix_href(href: str) -> str:
    """Return a cleaned version of a single href value, or the original if unchanged."""
    orig = href

    # 1. Strip concatenated absolute-URL tail:
    #    /foo-barhttps://example.com/foo-bar → /foo-bar
    href = re.sub(r"(https?:|www\.)\S+", "", href)

    # 2. URL-decode percent-encoded sequences (spaces → remove, leaving adjacent chars)
    decoded = urllib.parse.unquote(href)
    if decoded != href:
        # Remove any space chars that appeared after decoding, collapse double-hyphens
        decoded = decoded.replace(" ", "").replace("--", "-")
        href = decoded

    # 3. Strip .php extension
    href = re.sub(r"\.php([/?#]|$)", r"\1", href)

    # 4. Collapse literal spaces (e.g. an accidental space that wasn't %-encoded)
    if " " in href:
        href = href.replace(" ", "")
        href = href.replace("--", "-")

    # 5. Known compound-slug typos
    for bad, good in SLUG_TYPOS:
        href = href.replace(bad, good)

    # 6. Known wrong-route aliases
    if href == "/place-order":
        href = "/order"

    return href if href != orig else orig


def _fix_html(html: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Fix all href attributes in an HTML string.
    Returns (fixed_html, [(old_href, new_href), ...]).
    """
    changes: list[tuple[str, str]] = []

    def replacer(m: re.Match) -> str:
        href = m.group(1)
        # Only touch relative internal paths
        if not href.startswith("/") or href.startswith("//"):
            return m.group(0)
        # Skip already-correct routed paths and non-page paths
        if re.match(r"^/(blog|services|legal|media|static|assets)/", href):
            return m.group(0)
        fixed = _fix_href(href)
        if fixed != href:
            changes.append((href, fixed))
            return f'href="{fixed}"'
        return m.group(0)

    fixed_html = re.sub(r'href="([^"]*)"', replacer, html)
    return fixed_html, changes


class Command(BaseCommand):
    help = "Fix broken/encoded internal links in blog and service page paragraph HTML"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without writing to the database",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be saved"))

        from cms_blog.models import BlogPostPage
        from cms_service_pages.models import ServicePage

        page_sets = [
            ("BlogPostPage",  BlogPostPage.objects.all()),
            ("ServicePage",   ServicePage.objects.all()),
        ]

        total_pages   = 0
        total_changes = 0

        for model_name, qs in page_sets:
            for page in qs:
                page_dirty = False
                new_body   = list(page.body.raw_data)  # mutable copy

                for block in new_body:
                    if block.get("type") != "paragraph":
                        continue
                    html = block.get("value", "")
                    if not isinstance(html, str):
                        continue
                    fixed, changes = _fix_html(html)
                    if changes:
                        block["value"] = fixed
                        page_dirty = True
                        total_changes += len(changes)
                        for old, new in changes:
                            self.stdout.write(
                                f"  [{model_name}] {page.slug!r:45s}  "
                                f"{old!r} → {new!r}"
                            )

                if page_dirty and not dry_run:
                    page.body = new_body
                    page.save_revision().publish()
                    total_pages += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"\nDRY RUN complete — would fix {total_changes} link(s) across pages"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nFixed {total_changes} link(s) across {total_pages} page(s)"
            ))

"""
Fix absolute same-site links in all live CMS body content.

Transforms applied (in order, on raw JSON):
  1. Strip domain prefix: https://nursemygrade.com/X  →  /X
  2. Normalise legacy path aliases (.php, order fragments, etc.)
  3. Map old root-level service slugs: /slug  →  /services/slug
     (only for slugs that exist as live ServicePage records)
  4. Map old root-level blog slugs: /slug  →  /blog/slug
     (only for slugs that exist as live BlogPostPage records)
  5. Apply hardcoded legacy → new service path aliases (old URLs that differ
     from the current ServicePage slug).

Run with --dry-run first to preview changes.
Usage:
    python manage.py fix_cms_links --dry-run
    python manage.py fix_cms_links
    python manage.py fix_cms_links --site essaymaniacs.com
"""

import json
import re

from django.core.management.base import BaseCommand

from cms_blog.models import BlogPostPage
from cms_service_pages.models import ServicePage
from wagtail.models import Site

DOMAINS = [
    "nursemygrade.com",
    "essaymaniacs.com",
    "researchpapermate.com",
    "gradecrest.com",
    "writerscreek.com",
]

_DOMAIN_PAT = re.compile(
    r"https?://(?:www\.)?(?:" + "|".join(DOMAINS) + r")((?:/[^\s\"'<>]*)?)(?=[\"'<>\s]|$)"
)

# Legacy path substitutions: exact href="<old>" → href="<new>" replacements.
# IMPORTANT: these must be EXACT paths (no prefix matching) to avoid corrupting
# longer paths that share a prefix. Applied as regex anchored to the closing quote.
_LEGACY_PATHS = [
    # Order page aliases
    ("/place-order.php",  "/order"),
    ("/place-order",      "/order"),
    ("/order-now",        "/order"),
    ("/#order_here",      "/order"),
    ("/#order",           "/order"),
    # Other static page aliases
    ("/services.php",     "/services"),
    ("/blog.php",         "/blog"),
    # Common old service URL patterns that are EXACT paths differing from current slugs.
    # Only list paths that are the COMPLETE old URL, not prefixes.
    ("/essay-writing",               "/services/essays"),
    ("/essay-writing-service",       "/services/essays"),
    ("/write-my-essay",              "/services/essays"),
    ("/buy-essay",                   "/services/essays"),
    ("/research-paper-writing",      "/services/research-papers"),
    ("/research-paper-writing-service", "/services/research-papers"),
    ("/write-my-research-paper",     "/services/research-papers"),
    ("/dissertation-writing",        "/services/dissertations"),
    ("/dissertation-writing-service","/services/dissertations"),
    ("/thesis-writing-service",      "/services/dissertations"),
    ("/nursing-essay-writing",       "/services/online-nursing-essays-help"),
    ("/nursing-essay-writing-service", "/services/online-nursing-essays-help"),
    ("/nursing-assignment-help",     "/services/online-nursing-essays-help"),
    ("/nursing-care-plan-writing",   "/services/nursing-care-plan-writing-services"),
    ("/soap-note-writing",           "/services/nursing-soap-note-writing-help"),
    ("/term-paper-writing",          "/services/term-papers"),
    ("/term-paper-writing-service",  "/services/term-papers"),
    ("/case-study-writing",          "/services/case-studies"),
    ("/case-study-writing-service",  "/services/case-studies"),
    ("/coursework-writing-service",  "/services/coursework"),
    ("/do-my-coursework",            "/services/coursework"),
    ("/literature-review-writing",   "/services/literature-reviews"),
    ("/literature-review-writing-service", "/services/literature-reviews"),
    ("/editing-proofreading-service", "/services/proofreading"),
    ("/essay-editing-service",       "/services/proofreading"),
    ("/proofreading-service",        "/services/proofreading"),
    ("/admission-essay-writing",     "/services/admission-essays"),
    ("/personal-statement-writing",  "/services/personal-statements"),
    ("/college-essay-writing-service", "/services/admission-essays"),
    ("/data-analysis-help",          "/services/data-analysis"),
    ("/statistical-analysis-service", "/services/data-analysis"),
    ("/presentation-writing-service", "/services/presentations"),
    ("/take-my-online-class",        "/services/coursework"),
]

# Matches href="/{slug}" (and the JSON-escaped form href=\"/{slug}\") with an
# optional trailing slash.  The two (\\?) groups capture any backslash that
# json.dumps inserts before each quote so the replacement can mirror it.
_ROOT_HREF_PAT = re.compile(r'href=(\\?)"/([\w-]+)/?(\\?)"')


def _site_root(hostname):
    try:
        return Site.objects.get(hostname=hostname).root_page
    except Site.DoesNotExist:
        return None


def _build_service_slugs(site_filter=None):
    qs = ServicePage.objects.filter(live=True)
    if site_filter:
        root = _site_root(site_filter)
        if root:
            qs = qs.descendant_of(root)
    return set(qs.values_list("slug", flat=True))


def _build_blog_slugs(site_filter=None):
    qs = BlogPostPage.objects.filter(live=True)
    if site_filter:
        root = _site_root(site_filter)
        if root:
            qs = qs.descendant_of(root)
    return set(qs.values_list("slug", flat=True))


def _fix(raw: str, blog_slugs: set, service_slugs: set) -> str:
    # 1. Strip domain prefix from absolute same-site links only
    raw = _DOMAIN_PAT.sub(lambda m: m.group(1) or "/", raw)

    # 2. Apply legacy path substitutions — anchored to a non-slug character so
    #    we never match a prefix of a longer path. In JSON, href values end with
    #    \" (backslash + quote) so the lookahead must accept anything that is not
    #    a valid slug char [a-z0-9-]. This handles both JSON-escaped strings and
    #    plain unescaped href attributes.
    for old, new in _LEGACY_PATHS:
        pattern = re.escape(old) + r'(?=[^a-z0-9-])'
        raw = re.sub(pattern, new, raw)

    # Strip remaining *.php from same-site paths (after domain was stripped)
    raw = re.sub(r'"(/[a-z0-9/-]+)\.php(?=["\s])', lambda m: '"' + m.group(1), raw)

    # 3 & 4. Remap root-level hrefs: href="/{slug}" → /services/ or /blog/
    #    _ROOT_HREF_PAT already anchors on the closing quote, so no prefix risk.
    def _remap(m):
        q1, slug, q2 = m.group(1), m.group(2), m.group(3)
        if slug in service_slugs:
            return f'href={q1}"/services/{slug}{q2}"'
        if slug in blog_slugs:
            return f'href={q1}"/blog/{slug}{q2}"'
        return m.group(0)

    raw = _ROOT_HREF_PAT.sub(_remap, raw)
    return raw


def _get_raw(page) -> str:
    return json.dumps(
        [
            {"type": b.block_type, "value": b.block.get_prep_value(b.value), "id": str(b.id)}
            for b in page.body
        ]
    )


class Command(BaseCommand):
    help = (
        "Fix flat/absolute same-site links in all live CMS pages — "
        "strips domain prefixes, applies legacy aliases, and prefixes "
        "/services/ and /blog/ on bare root-level slugs."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving.",
        )
        parser.add_argument(
            "--site",
            default=None,
            help="Restrict to a single site hostname, e.g. essaymaniacs.com",
        )

    def handle(self, *_args, **options):
        dry = options["dry_run"]
        site_filter = options.get("site")

        service_slugs = _build_service_slugs(site_filter)
        blog_slugs = _build_blog_slugs(site_filter)
        self.stdout.write(
            f"Service slugs: {len(service_slugs)} | Blog slugs: {len(blog_slugs)}"
            + (f" (site={site_filter})" if site_filter else " (all sites)")
        )

        svc_fixed = blog_fixed = 0

        qs_svc  = ServicePage.objects.filter(live=True)
        qs_blog = BlogPostPage.objects.filter(live=True)
        if site_filter:
            root = _site_root(site_filter)
            if root:
                qs_svc  = qs_svc.descendant_of(root)
                qs_blog = qs_blog.descendant_of(root)

        pages = list(qs_svc) + list(qs_blog)
        self.stdout.write(f"Pages to scan: {len(pages)}")

        for page in pages:
            try:
                raw = _get_raw(page)
            except Exception as exc:
                self.stderr.write(f"  ERROR reading {page.slug!r}: {exc}")
                continue

            fixed = _fix(raw, blog_slugs, service_slugs)
            if fixed == raw:
                continue

            label = f"{page.__class__.__name__} slug={page.slug!r}"
            if dry:
                # Show a diff excerpt
                for old, new in [(raw[i:i+80], fixed[i:i+80]) for i in range(0, min(len(raw), 400), 80)]:
                    if old != new:
                        self.stdout.write(f"  [dry] {label}")
                        self.stdout.write(f"        before: ...{old}...")
                        self.stdout.write(f"        after:  ...{new}...")
                        break
                else:
                    self.stdout.write(f"  [dry] would fix {label}")
            else:
                page.body = json.loads(fixed)
                page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  fixed {label}"))

            if isinstance(page, ServicePage):
                svc_fixed += 1
            else:
                blog_fixed += 1

        verb = "Would fix" if dry else "Fixed"
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{verb}: {svc_fixed} service pages, {blog_fixed} blog posts"
            )
        )
        if dry:
            self.stdout.write("Run without --dry-run to apply changes.")

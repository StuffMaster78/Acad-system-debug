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
    # Old service URL aliases — map to the canonical service slug (flat, no /services/ prefix).
    ("/essay-writing-service",       "/essays"),
    ("/write-my-essay",              "/essays"),
    ("/buy-essay",                   "/essays"),
    ("/research-paper-writing",      "/research-papers"),
    ("/research-paper-writing-service", "/research-papers"),
    ("/write-my-research-paper",     "/research-papers"),
    ("/dissertation-writing",        "/dissertations"),
    ("/dissertation-writing-service","/dissertations"),
    ("/thesis-writing-service",      "/dissertations"),
    ("/nursing-essay-writing",       "/online-nursing-essays-help"),
    ("/nursing-essay-writing-service", "/online-nursing-essays-help"),
    ("/nursing-care-plan-writing",   "/nursing-care-plan-writing-services"),
    ("/soap-note-writing",           "/nursing-soap-note-writing-help"),
    ("/term-paper-writing",          "/term-papers"),
    ("/term-paper-writing-service",  "/term-papers"),
    ("/case-study-writing",          "/case-studies"),
    ("/case-study-writing-service",  "/case-studies"),
    ("/coursework-writing-service",  "/coursework"),
    ("/do-my-coursework",            "/coursework"),
    ("/literature-review-writing",   "/literature-reviews"),
    ("/literature-review-writing-service", "/literature-reviews"),
    ("/editing-proofreading-service", "/editing-proofreading"),
    ("/essay-editing-service",       "/editing-proofreading"),
    ("/proofreading-service",        "/editing-proofreading"),
    ("/admission-essay-writing",     "/admission-essays"),
    ("/personal-statement-writing",  "/personal-statements"),
    ("/college-essay-writing-service", "/admission-essays"),
    ("/data-analysis-help",          "/data-analysis"),
    ("/statistical-analysis-service", "/data-analysis"),
    ("/presentation-writing-service", "/presentations"),
    ("/take-my-online-class",        "/online-class-help"),
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

    # 3. Flatten any previously-written /services/slug → /slug (Option B: flat URLs).
    _SVC_HREF_PAT = re.compile(r'href=(\\?)"/services/([\w-]+)/?(\\?)"')
    def _flatten_svc(m):
        q1, slug, q2 = m.group(1), m.group(2), m.group(3)
        if slug in service_slugs:
            return f'href={q1}"/{slug}{q2}"'
        return m.group(0)
    raw = _SVC_HREF_PAT.sub(_flatten_svc, raw)

    # 4. Remap any remaining root-level single-segment hrefs to /blog/ or flat.
    def _remap(m):
        q1, slug, q2 = m.group(1), m.group(2), m.group(3)
        if slug in service_slugs:
            return f'href={q1}"/{slug}{q2}"'
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

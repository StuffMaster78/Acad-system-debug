"""
Fix absolute same-site links in all live CMS body content.

Transforms applied (in order, on raw JSON):
  1. Strip domain prefix: https://nursemygrade.com/X  →  /X
  2. Normalise legacy path aliases (.php, order fragments, etc.)
  3. Map old root-level blog slugs: /some-slug  →  /blog/some-slug
     (only for slugs that exist as live BlogPostPage records)
"""

import json
import re

from django.core.management.base import BaseCommand

from cms_blog.models import BlogPostPage
from cms_service_pages.models import ServicePage

DOMAINS = [
    "nursemygrade.com",
    "essaymaniacs.com",
    "researchpapermate.com",
    "gradecrest.com",
]

_DOMAIN_PAT = re.compile(
    r"https?://(?:www\.)?(?:" + "|".join(DOMAINS) + r")((?:/[^\s\"'<>]*)?)(?=[\"'<>\s]|$)"
)

# Legacy path substitutions applied as plain string replacements (order matters).
_LEGACY = [
    ("/place-order.php", "/order"),
    ("/place-order",     "/order"),
    ("/order-now",       "/order"),
    ("/#order_here",     "/order"),
    ("/#order",          "/order"),
    ("/services.php",    "/services"),
    ("/blog.php",        "/blog"),
]

# Matches href="/slug" where slug has no sub-path (old root-level paths).
_ROOT_HREF_PAT = re.compile(r'href="/([\w-]+)"')


def _build_blog_slugs():
    return set(BlogPostPage.objects.filter(live=True).values_list("slug", flat=True))


def _fix(raw: str, blog_slugs: set) -> str:
    # 1. Strip domain
    raw = _DOMAIN_PAT.sub(lambda m: m.group(1) or "/", raw)

    # 2. Legacy paths
    for old, new in _LEGACY:
        raw = raw.replace(old, new)

    # Strip remaining *.php from same-site paths (after domain was removed above)
    raw = re.sub(r'"(/[a-z0-9/-]+)\.php(?=["\s])', lambda m: '"' + m.group(1), raw)

    # 3. Remap root-level blog hrefs: href="/slug" → href="/blog/slug"
    def _remap(m):
        slug = m.group(1)
        return f'href="/blog/{slug}"' if slug in blog_slugs else m.group(0)

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
    help = "Strip absolute same-site links and fix legacy paths in all live CMS pages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving anything",
        )

    def handle(self, *_args, **options):
        dry = options["dry_run"]
        blog_slugs = _build_blog_slugs()
        self.stdout.write(f"Blog slugs loaded: {len(blog_slugs)}")

        svc_fixed = blog_fixed = 0

        pages = list(ServicePage.objects.filter(live=True)) + list(
            BlogPostPage.objects.filter(live=True)
        )
        self.stdout.write(f"Pages to scan: {len(pages)}")

        for page in pages:
            raw = _get_raw(page)
            fixed = _fix(raw, blog_slugs)
            if fixed == raw:
                continue
            label = f"{page.__class__.__name__} slug={page.slug!r}"
            if dry:
                self.stdout.write(f"  [dry] would fix {label}")
            else:
                page.body = json.loads(fixed)
                page.save_revision().publish()
                self.stdout.write(f"  fixed {label}")
            if isinstance(page, ServicePage):
                svc_fixed += 1
            else:
                blog_fixed += 1

        verb = "Would fix" if dry else "Fixed"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb}: {svc_fixed} service pages, {blog_fixed} blog posts"
            )
        )

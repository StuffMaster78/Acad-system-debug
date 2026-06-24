"""
Management command: assign_featured_images
==========================================

Downloads images from a URL and assigns them as featured images to
BlogPostPage and ServicePage objects that currently have none.

Modes
-----
--report
    List every page (blog + services) that is missing a featured image.
    No changes are made.

--placeholder
    Assign picsum.photos placeholder images (deterministic per slug, no
    API key required).  Safe to run multiple times — skips pages that
    already have an image unless --force is given.

--from-file=path/to/mapping.json
    Read a JSON file of the form::

        {
          "blog":     { "slug": "https://..." },
          "services": { "slug": "https://..." }
        }

    Downloads each URL and assigns to the matching page.  Entries whose
    page does not exist are silently skipped.

Options
-------
--site DOMAIN     Filter to a single website (default: all sites).
--force           Overwrite existing images.
--dry-run         Print what would happen without downloading or saving.

Usage
-----
    python manage.py assign_featured_images --report
    python manage.py assign_featured_images --report --site nursemygrade.com

    python manage.py assign_featured_images --placeholder
    python manage.py assign_featured_images --placeholder --site nursemygrade.com --dry-run

    python manage.py assign_featured_images --from-file=images.json
    python manage.py assign_featured_images --from-file=images.json --force
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):
    help = "Assign featured images to blog posts and service pages."

    def add_arguments(self, parser: CommandParser) -> None:
        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument("--report",      action="store_true",  help="List pages missing featured images.")
        mode.add_argument("--placeholder", action="store_true",  help="Assign picsum.photos placeholders.")
        mode.add_argument("--from-file",   dest="from_file",     metavar="PATH", help="JSON mapping file.")
        mode.add_argument("--scrape-live", action="store_true",  help="Scrape og:image from each page's live URL.")

        parser.add_argument("--site",    default=None, help="Filter by domain (e.g. nursemygrade.com).")
        parser.add_argument("--force",   action="store_true", help="Overwrite existing images.")
        parser.add_argument("--dry-run", action="store_true", help="Print actions without saving.")
        parser.add_argument("--delay",   type=float, default=0.5, help="Seconds between requests (default 0.5).")

    # ── entry point ──────────────────────────────────────────────────────────

    def handle(self, **options) -> None:
        site_domain: Optional[str] = options["site"]
        force:       bool          = options["force"]
        dry_run:     bool          = options["dry_run"]
        delay:       float         = options["delay"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be saved.\n"))

        blog_pages    = self._get_blog_pages(site_domain, force)
        service_pages = self._get_service_pages(site_domain, force)

        if options["report"]:
            self._report(blog_pages, service_pages)
            return

        if options["placeholder"]:
            self._assign_placeholder(blog_pages, service_pages, dry_run)
            return

        if options["from_file"]:
            mapping = self._load_mapping(options["from_file"])
            self._assign_from_mapping(blog_pages, service_pages, mapping, force, dry_run)

        if options["scrape_live"]:
            self._scrape_live(blog_pages, service_pages, dry_run, delay)

    # ── mode: report ─────────────────────────────────────────────────────────

    def _report(self, blog_pages, service_pages) -> None:
        self.stdout.write("\n" + self.style.HTTP_INFO("=== Blog posts missing featured_image ==="))
        if blog_pages:
            for p in blog_pages:
                self.stdout.write(f"  blog  {p.slug:<55} [{p.get_site().hostname}]")
        else:
            self.stdout.write(self.style.SUCCESS("  All blog posts have images. ✓"))

        self.stdout.write("\n" + self.style.HTTP_INFO("=== Service pages missing og_image ==="))
        if service_pages:
            for p in service_pages:
                self.stdout.write(f"  svc   {p.slug:<55} [{p.get_site().hostname}]")
        else:
            self.stdout.write(self.style.SUCCESS("  All service pages have images. ✓"))

        total = len(blog_pages) + len(service_pages)
        self.stdout.write(f"\nTotal missing: {total}\n")

    # ── mode: placeholder ────────────────────────────────────────────────────

    def _assign_placeholder(self, blog_pages, service_pages, dry_run: bool) -> None:
        import hashlib

        ok = err = skip = 0

        pages = [("blog", p) for p in blog_pages] + [("svc", p) for p in service_pages]
        total = len(pages)

        for i, (kind, page) in enumerate(pages, 1):
            seed = hashlib.md5(page.slug.encode()).hexdigest()[:8]
            url = f"https://picsum.photos/seed/{seed}/1200/630"
            label = f"[{i}/{total}] {kind} {page.slug}"

            if dry_run:
                self.stdout.write(f"  {label}  →  {url}")
                ok += 1
                continue

            try:
                img = self._download_and_create_image(
                    url=url,
                    title=f"Featured image — {page.title}",
                    filename=f"{page.slug}-featured.jpg",
                )
                self._assign_image(kind, page, img)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {label}"))
                ok += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  ✗ {label}: {exc}"))
                err += 1

        self.stdout.write(f"\nDone — {ok} assigned, {err} errors, {skip} skipped.")

    # ── mode: from-file ──────────────────────────────────────────────────────

    def _assign_from_mapping(self, blog_pages, service_pages, mapping: dict, force: bool, dry_run: bool) -> None:
        blog_index = {p.slug: p for p in blog_pages}
        svc_index  = {p.slug: p for p in service_pages}

        # Also include pages that already have images when --force
        if force:
            from cms_blog.models import BlogPostPage
            from cms_service_pages.models import ServicePage
            for p in BlogPostPage.objects.live():
                blog_index.setdefault(p.slug, p)
            for p in ServicePage.objects.live():
                svc_index.setdefault(p.slug, p)

        ok = err = skip = 0
        entries = (
            [("blog", slug, url) for slug, url in mapping.get("blog", {}).items()] +
            [("svc",  slug, url) for slug, url in mapping.get("services", {}).items()]
        )

        for kind, slug, url in entries:
            index = blog_index if kind == "blog" else svc_index
            page  = index.get(slug)
            label = f"{kind} {slug}"

            if page is None:
                self.stdout.write(self.style.WARNING(f"  – {label}: page not found, skipping"))
                skip += 1
                continue

            if dry_run:
                self.stdout.write(f"  {label}  →  {url}")
                ok += 1
                continue

            try:
                fname = self._filename_from_url(url, slug)
                img   = self._download_and_create_image(
                    url=url,
                    title=f"Featured image — {page.title}",
                    filename=fname,
                )
                self._assign_image(kind, page, img)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {label}"))
                ok += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  ✗ {label}: {exc}"))
                err += 1

        self.stdout.write(f"\nDone — {ok} assigned, {err} errors, {skip} skipped.")

    # ── mode: scrape-live ────────────────────────────────────────────────────

    def _scrape_live(self, blog_pages, service_pages, dry_run: bool, delay: float) -> None:
        """
        For each page, hit its live URL, parse og:image from the <head>,
        download that image, and assign it as featured_image / og_image.
        """
        import re
        import time
        import requests

        OG_RE = re.compile(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            re.IGNORECASE,
        )
        # Also handle reversed attribute order: content=... property=...
        OG_RE2 = re.compile(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            re.IGNORECASE,
        )

        def extract_og_image(html_head: str) -> str | None:
            m = OG_RE.search(html_head) or OG_RE2.search(html_head)
            return m.group(1) if m else None

        pages = [("blog", p) for p in blog_pages] + [("svc", p) for p in service_pages]
        total = len(pages)
        ok = err = skip = 0

        self.stdout.write(f"Scraping {total} live pages (delay={delay}s)…\n")

        for i, (kind, page) in enumerate(pages, 1):
            try:
                site     = page.get_site()
                hostname = site.hostname
            except Exception:
                self.stdout.write(self.style.WARNING(f"  – [{i}/{total}] {page.slug}: no site found"))
                skip += 1
                continue

            prefix   = "blog" if kind == "blog" else "services"
            live_url = f"https://{hostname}/{prefix}/{page.slug}/"
            label    = f"[{i}/{total}] {kind} {page.slug}"

            # Fetch only the first 20 KB — og:image is always in <head>
            try:
                resp = requests.get(
                    live_url, timeout=15, stream=True,
                    headers={"User-Agent": "WritingSystemBot/1.0"},
                )
                resp.raise_for_status()
                chunk = b""
                for part in resp.iter_content(4096):
                    chunk += part
                    if len(chunk) >= 20_000:
                        break
                resp.close()
                html_head = chunk.decode("utf-8", errors="replace")
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"  – {label}: fetch failed — {exc}"))
                err += 1
                time.sleep(delay)
                continue

            img_url = extract_og_image(html_head)
            if not img_url:
                self.stdout.write(self.style.WARNING(f"  – {label}: no og:image in <head>"))
                skip += 1
                time.sleep(delay)
                continue

            if dry_run:
                self.stdout.write(f"  {label}  →  {img_url}")
                ok += 1
                time.sleep(delay * 0.2)
                continue

            try:
                fname = self._filename_from_url(img_url, page.slug)
                img   = self._download_and_create_image(
                    url=img_url,
                    title=f"Featured image — {page.title}",
                    filename=fname,
                )
                self._assign_image(kind, page, img)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {label}"))
                ok += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  ✗ {label}: {exc}"))
                err += 1

            time.sleep(delay)

        self.stdout.write(f"\nDone — {ok} assigned, {err} errors, {skip} no-image.\n")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_blog_pages(self, site_domain: Optional[str], force: bool):
        from cms_blog.models import BlogPostPage
        from django.db import connection as _conn
        from wagtail.models import Site

        # Defer fields that may not exist in partially-migrated DBs
        with _conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cms_blog_blogpostpage'"
            )
            existing_cols = {r[0] for r in cur.fetchall()}
        defer_fields = [
            f.name for f in BlogPostPage._meta.get_fields()
            if hasattr(f, 'column') and f.column not in existing_cols
        ]

        qs = BlogPostPage.objects.live().defer(*defer_fields) if defer_fields else BlogPostPage.objects.live()
        if site_domain:
            try:
                site = Site.objects.get(hostname=site_domain)
                qs = qs.filter(path__startswith=site.root_page.path)
            except Site.DoesNotExist:
                raise CommandError(f"No Wagtail site found for domain '{site_domain}'.")
        if not force:
            qs = qs.filter(featured_image__isnull=True)
        return list(qs.order_by("slug"))

    def _get_service_pages(self, site_domain: Optional[str], force: bool):
        from cms_service_pages.models import ServicePage
        qs = ServicePage.objects.live()
        if site_domain:
            from wagtail.models import Site
            try:
                site = Site.objects.get(hostname=site_domain)
                qs = qs.filter(path__startswith=site.root_page.path)
            except Site.DoesNotExist:
                raise CommandError(f"No Wagtail site found for domain '{site_domain}'.")
        if not force:
            qs = qs.filter(og_image__isnull=True)
        return list(qs.order_by("slug"))

    @staticmethod
    def _download_and_create_image(url: str, title: str, filename: str):
        import requests
        from wagtail.images import get_image_model

        Image = get_image_model()

        resp = requests.get(url, timeout=30, headers={"User-Agent": "WritingSystemBot/1.0"})
        resp.raise_for_status()

        img = Image(title=title)
        img.file.save(filename, ContentFile(resp.content), save=True)
        return img

    @staticmethod
    def _assign_image(kind: str, page, img) -> None:
        if kind == "blog":
            page.featured_image = img
        else:
            page.og_image = img
        page.save_revision().publish()

    @staticmethod
    def _load_mapping(filepath: str) -> dict:
        path = Path(filepath)
        if not path.exists():
            raise CommandError(f"File not found: {filepath}")
        with path.open() as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as exc:
                raise CommandError(f"Invalid JSON in {filepath}: {exc}") from exc

    @staticmethod
    def _filename_from_url(url: str, slug: str) -> str:
        parsed = urlparse(url)
        ext    = os.path.splitext(parsed.path)[1]
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".avif"}:
            ext = ".jpg"
        return f"{slug}-featured{ext}"

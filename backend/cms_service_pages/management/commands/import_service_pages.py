"""
import_service_pages — import scraped service page content into Wagtail ServicePage

Reads a JSON file produced by scripts/scrape_live_services.py and creates
(or optionally updates) published ServicePage objects under the site's
ServiceIndexPage.

JSON schema (each item — all fields from the scraper):
    {
        "slug":               "essay-writing",
        "title":              "Essay Writing Service",
        "seo_title":          "Essay Writing Service from $13/Page | GradeCrest",
        "search_description": "Get a custom essay written …",
        "hero_headline":      "Essay Writing Service",
        "excerpt":            "Short description …",   ← ignored (no field on ServicePage)
        "reading_time":       5,                        ← ignored
        "body_html":          "<h2>…</h2><p>…</p>"
    }

The scraper sets hero_headline = title (H1 text).  Fields not in the JSON
(pricing_from, includes_items, delivers_items, etc.) are left at their
current values so the command is safe to run after seed_gradecrest_services.

Usage:
    python manage.py import_service_pages --site gradecrest.com --file /tmp/gc_services.json
    python manage.py import_service_pages --site gradecrest.com --file /tmp/gc_services.json --update
    python manage.py import_service_pages --site nursemygrade.com --file /tmp/nmg_services.json
"""

from __future__ import annotations

import json
import os

from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):
    help = "Import scraped service page content from a JSON file into Wagtail."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--site",
            required=True,
            help="Site hostname (e.g. gradecrest.com). Must match a Wagtail Site.",
        )
        parser.add_argument(
            "--file",
            required=True,
            help="Path to JSON file produced by scrape_live_services.py.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            default=False,
            help="Overwrite body/title/SEO on pages that already exist (default: skip).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print what would happen without writing to the database.",
        )

    def handle(self, *args, **options):
        from wagtail.models import Site
        from cms_service_pages.models import ServiceIndexPage

        site_domain = options["site"]
        json_path = options["file"]
        do_update = options["update"]
        dry_run = options["dry_run"]

        if not os.path.exists(json_path):
            raise CommandError(f"File not found: {json_path}")

        with open(json_path, encoding="utf-8") as f:
            pages = json.load(f)

        if not isinstance(pages, list):
            raise CommandError("JSON must be a top-level array of page objects.")

        self.stdout.write(f"Loaded {len(pages)} pages from {json_path}")

        try:
            site = Site.objects.get(hostname=site_domain)
        except Site.DoesNotExist:
            available = list(Site.objects.values_list("hostname", flat=True))
            raise CommandError(
                f"No Wagtail site found for '{site_domain}'. Available: {available}"
            )

        svc_index = (
            ServiceIndexPage.objects.live()
            .descendant_of(site.root_page)
            .first()
        )
        if not svc_index:
            raise CommandError(
                f"No live ServiceIndexPage found under '{site.root_page}'. "
                "Run setup_tenants (or create one in Wagtail admin) first."
            )

        self.stdout.write(
            f"Target: {site_domain} → ServiceIndexPage id={svc_index.pk} "
            f"({svc_index.title!r})"
        )
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no database writes."))

        created = updated = skipped = errors = 0

        for idx, item in enumerate(pages, start=1):
            try:
                result = self._import_page(
                    item=item,
                    svc_index=svc_index,
                    do_update=do_update,
                    dry_run=dry_run,
                )
                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
                else:
                    skipped += 1
            except Exception as exc:
                errors += 1
                slug = item.get("slug", f"[item {idx}]")
                self.stderr.write(self.style.ERROR(f"  ERROR {slug}: {exc}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created={created} Updated={updated} "
                f"Skipped={skipped} Errors={errors}"
            )
        )

    def _import_page(self, *, item: dict, svc_index, do_update: bool, dry_run: bool) -> str:
        from cms_service_pages.models import ServicePage

        slug = (item.get("slug") or "").strip()
        title = (item.get("title") or slug).strip()

        if not slug:
            raise ValueError("Item has no slug.")

        existing = ServicePage.objects.descendant_of(svc_index).filter(slug=slug).first()

        if existing and not do_update:
            self.stdout.write(f"  SKIP  {slug}")
            return "skipped"

        body_blocks = self._html_to_body(item.get("body_html", ""))

        if existing:
            if not dry_run:
                existing.title = title
                existing.seo_title = item.get("seo_title", title)
                existing.search_description = item.get("search_description", "")[:255]
                existing.hero_headline = item.get("hero_headline", title)
                existing.body = body_blocks
                existing.save_revision().publish()
            self.stdout.write(self.style.WARNING(f"  {'(dry) ' if dry_run else ''}UPDATE {slug}"))
            return "updated"

        if not dry_run:
            page = ServicePage(
                title=title,
                slug=slug,
                seo_title=item.get("seo_title", title),
                search_description=item.get("search_description", "")[:255],
                hero_headline=item.get("hero_headline", title),
                body=body_blocks,
                live=True,
            )
            svc_index.add_child(instance=page)
            page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS(f"  {'(dry) ' if dry_run else ''}CREATE {slug}"))
        return "created"

    @staticmethod
    def _html_to_body(html: str) -> list:
        html = (html or "").strip()
        if not html:
            return []
        return [{"type": "paragraph", "value": html}]

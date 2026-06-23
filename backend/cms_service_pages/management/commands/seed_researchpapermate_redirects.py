"""
Management command: seed_researchpapermate_redirects
====================================================

Creates 301 redirects from old flat ResearchPaperMate URL paths to the
new /services/ structure.

Usage:
    python manage.py seed_researchpapermate_redirects
    python manage.py seed_researchpapermate_redirects --site researchpapermate.com
"""

from django.core.management.base import BaseCommand, CommandParser

REDIRECTS = [
    # ── Research papers ─────────────────────────────────────────────────────
    ("/research-papers",                "/services/research-papers"),
    ("/research-paper",                 "/services/research-papers"),
    ("/research-paper-writing",         "/services/research-papers"),
    ("/research-paper-writing-service", "/services/research-papers"),
    ("/write-my-research-paper",        "/services/research-papers"),
    ("/buy-research-paper",             "/services/research-papers"),

    # ── Essays ──────────────────────────────────────────────────────────────
    ("/essays",                         "/services/essays"),
    ("/essay-writing",                  "/services/essays"),
    ("/essay-writing-service",          "/services/essays"),
    ("/write-my-essay",                 "/services/essays"),

    # ── Dissertations ───────────────────────────────────────────────────────
    ("/dissertations",                  "/services/dissertations"),
    ("/dissertation-writing",           "/services/dissertations"),
    ("/dissertation-writing-service",   "/services/dissertations"),
    ("/thesis-writing",                 "/services/dissertations"),
    ("/thesis-writing-service",         "/services/dissertations"),

    # ── Case studies ────────────────────────────────────────────────────────
    ("/case-studies",                   "/services/case-studies"),
    ("/case-study",                     "/services/case-studies"),
    ("/case-study-writing",             "/services/case-studies"),
    ("/case-study-writing-service",     "/services/case-studies"),

    # ── Coursework ──────────────────────────────────────────────────────────
    ("/coursework",                     "/services/coursework"),
    ("/coursework-help",                "/services/coursework"),
    ("/coursework-writing-service",     "/services/coursework"),
    ("/assignment-help",                "/services/coursework"),

    # ── Data analysis ───────────────────────────────────────────────────────
    ("/data-analysis",                  "/services/data-analysis"),
    ("/data-analysis-help",             "/services/data-analysis"),
    ("/statistical-analysis",           "/services/data-analysis"),
    ("/statistics-help",                "/services/data-analysis"),

    # ── Literature reviews ──────────────────────────────────────────────────
    ("/literature-reviews",             "/services/literature-reviews"),
    ("/literature-review",              "/services/literature-reviews"),
    ("/literature-review-writing",      "/services/literature-reviews"),

    # ── Lab reports ─────────────────────────────────────────────────────────
    ("/lab-reports",                    "/services/lab-reports"),
    ("/lab-report",                     "/services/lab-reports"),
    ("/lab-report-writing",             "/services/lab-reports"),

    # ── Presentations ───────────────────────────────────────────────────────
    ("/presentations",                  "/services/presentations"),
    ("/presentation-writing",           "/services/presentations"),
    ("/presentation-help",              "/services/presentations"),

    # ── Generic old top-level pages ─────────────────────────────────────────
    ("/about-us",    "/about"),
    ("/contact-us",  "/contact"),
    ("/place-order", "/order"),
    ("/order-now",   "/order"),
]


class Command(BaseCommand):
    help = "Seed Wagtail 301 redirects from old ResearchPaperMate flat URLs to /services/ paths"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="researchpapermate.com")

    def handle(self, *args, **options):
        from wagtail.models import Site
        from wagtail.contrib.redirects.models import Redirect

        hostname = options["site"]

        try:
            site = Site.objects.get(hostname=hostname)
        except Site.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No site for '{hostname}'."))
            return

        created = skipped = 0

        for old_path, new_path in REDIRECTS:
            old_path_normalised = old_path.rstrip("/")
            if Redirect.objects.filter(site=site, old_path=old_path_normalised).exists():
                skipped += 1
                continue
            Redirect.objects.create(
                site=site,
                old_path=old_path_normalised,
                redirect_link=new_path,
                is_permanent=True,
            )
            self.stdout.write(self.style.SUCCESS(f"  CREATE  {old_path}  →  {new_path}"))
            created += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Done — {created} created, {skipped} skipped")
        )

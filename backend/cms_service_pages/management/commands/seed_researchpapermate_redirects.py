"""
Management command: seed_researchpapermate_redirects
====================================================

Creates 301 redirects from old flat ResearchPaperMate URL paths to the
new flat canonical URLs (/:slug).

Usage:
    python manage.py seed_researchpapermate_redirects
    python manage.py seed_researchpapermate_redirects --site researchpapermate.com
"""

from django.core.management.base import BaseCommand, CommandParser

REDIRECTS = [
    # ── Research papers ─────────────────────────────────────────────────────
    ("/research-papers",                "/research-papers"),
    ("/research-paper",                 "/research-papers"),
    ("/research-paper-writing",         "/research-papers"),
    ("/research-paper-writing-service", "/research-papers"),
    ("/write-my-research-paper",        "/research-papers"),
    ("/buy-research-paper",             "/research-papers"),

    # ── Essays ──────────────────────────────────────────────────────────────
    ("/essays",                         "/essays"),
    ("/essay-writing",                  "/essays"),
    ("/essay-writing-service",          "/essays"),
    ("/write-my-essay",                 "/essays"),

    # ── Dissertations ───────────────────────────────────────────────────────
    ("/dissertations",                  "/dissertations"),
    ("/dissertation-writing",           "/dissertations"),
    ("/dissertation-writing-service",   "/dissertations"),
    ("/thesis-writing",                 "/dissertations"),
    ("/thesis-writing-service",         "/dissertations"),

    # ── Case studies ────────────────────────────────────────────────────────
    ("/case-studies",                   "/case-studies"),
    ("/case-study",                     "/case-studies"),
    ("/case-study-writing",             "/case-studies"),
    ("/case-study-writing-service",     "/case-studies"),

    # ── Coursework ──────────────────────────────────────────────────────────
    ("/coursework",                     "/coursework"),
    ("/coursework-help",                "/coursework"),
    ("/coursework-writing-service",     "/coursework"),
    ("/assignment-help",                "/coursework"),

    # ── Data analysis ───────────────────────────────────────────────────────
    ("/data-analysis",                  "/data-analysis"),
    ("/data-analysis-help",             "/data-analysis"),
    ("/statistical-analysis",           "/data-analysis"),
    ("/statistics-help",                "/data-analysis"),

    # ── Literature reviews ──────────────────────────────────────────────────
    ("/literature-reviews",             "/literature-reviews"),
    ("/literature-review",              "/literature-reviews"),
    ("/literature-review-writing",      "/literature-reviews"),

    # ── Lab reports ─────────────────────────────────────────────────────────
    ("/lab-reports",                    "/lab-reports"),
    ("/lab-report",                     "/lab-reports"),
    ("/lab-report-writing",             "/lab-reports"),

    # ── Presentations ───────────────────────────────────────────────────────
    ("/presentations",                  "/presentations"),
    ("/presentation-writing",           "/presentations"),
    ("/presentation-help",              "/presentations"),

    # ── Generic old top-level pages ─────────────────────────────────────────
    ("/about-us",    "/about"),
    ("/contact-us",  "/contact"),
    ("/place-order", "/order"),
    ("/order-now",   "/order"),
]


class Command(BaseCommand):
    help = "Seed Wagtail 301 redirects from old ResearchPaperMate flat URLs to flat canonical paths (/:slug)"

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

"""
Management command: seed_essaymaniacs_redirects
===============================================

Creates 301 redirects in Wagtail from old flat EssayManiacs URL paths
to flat canonical URLs (/:slug).

Old site used root-level paths (/essay-writing, /research-paper, etc.).
New site uses /services/<slug>/.

Idempotent — skips redirects that already exist.

Usage:
    python manage.py seed_essaymaniacs_redirects
    python manage.py seed_essaymaniacs_redirects --site essaymaniacs.com
"""

from django.core.management.base import BaseCommand, CommandParser

REDIRECTS = [
    # ── Essay service variants ──────────────────────────────────────────────
    ("/essays",                        "/essays"),
    ("/essay-writing",                 "/essays"),
    ("/essay-writing-service",         "/essays"),
    ("/write-my-essay",                "/essays"),
    ("/buy-essay",                     "/essays"),
    ("/pay-for-essay",                 "/essays"),
    ("/cheap-essays",                  "/essays"),

    # ── Argumentative essays ────────────────────────────────────────────────
    ("/argumentative-essays",          "/argumentative-essays"),
    ("/argumentative-essay",           "/argumentative-essays"),
    ("/argumentative-essay-help",      "/argumentative-essays"),
    ("/write-my-argumentative-essay",  "/argumentative-essays"),

    # ── Research papers ─────────────────────────────────────────────────────
    ("/research-papers",               "/research-papers"),
    ("/research-paper",                "/research-papers"),
    ("/research-paper-writing",        "/research-papers"),
    ("/research-paper-writing-service","/research-papers"),
    ("/write-my-research-paper",       "/research-papers"),
    ("/buy-research-paper",            "/research-papers"),

    # ── Dissertations ───────────────────────────────────────────────────────
    ("/dissertations",                 "/dissertations"),
    ("/dissertation-writing",          "/dissertations"),
    ("/dissertation-writing-service",  "/dissertations"),
    ("/write-my-dissertation",         "/dissertations"),
    ("/thesis-writing",                "/dissertations"),
    ("/thesis-writing-service",        "/dissertations"),

    # ── Term papers ─────────────────────────────────────────────────────────
    ("/term-papers",                   "/term-papers"),
    ("/term-paper",                    "/term-papers"),
    ("/term-paper-writing",            "/term-papers"),
    ("/term-paper-writing-service",    "/term-papers"),

    # ── Case studies ────────────────────────────────────────────────────────
    ("/case-studies",                  "/case-studies"),
    ("/case-study",                    "/case-studies"),
    ("/case-study-writing",            "/case-studies"),
    ("/case-study-writing-service",    "/case-studies"),

    # ── Coursework / homework ───────────────────────────────────────────────
    ("/coursework",                    "/coursework"),
    ("/coursework-help",               "/coursework"),
    ("/coursework-writing-service",    "/coursework"),
    ("/do-my-coursework",              "/coursework"),
    ("/assignment-help",               "/coursework"),
    ("/homework-help",                 "/coursework"),

    # ── Admission / personal statements ────────────────────────────────────
    ("/admission-essays",              "/admission-essays"),
    ("/admission-essay",               "/admission-essays"),
    ("/admission-essay-writing",       "/admission-essays"),
    ("/college-essay-writing",         "/admission-essays"),
    ("/college-essay-writing-service", "/admission-essays"),
    ("/personal-statements",           "/personal-statements"),
    ("/personal-statement",            "/personal-statements"),
    ("/personal-statement-writing",    "/personal-statements"),

    # ── Scholarship essays ──────────────────────────────────────────────────
    ("/scholarship-essays",            "/scholarship-essays"),
    ("/scholarship-essay",             "/scholarship-essays"),
    ("/scholarship-essay-writing",     "/scholarship-essays"),

    # ── Literature reviews ──────────────────────────────────────────────────
    ("/literature-reviews",            "/literature-reviews"),
    ("/literature-review",             "/literature-reviews"),
    ("/literature-review-writing",     "/literature-reviews"),
    ("/literature-review-writing-service", "/literature-reviews"),

    # ── Annotated bibliographies ────────────────────────────────────────────
    ("/annotated-bibliographies",      "/annotated-bibliographies"),
    ("/annotated-bibliography",        "/annotated-bibliographies"),

    # ── Book reports ────────────────────────────────────────────────────────
    ("/book-reports",                  "/book-reports"),
    ("/book-report",                   "/book-reports"),
    ("/book-report-writing",           "/book-reports"),

    # ── Lab reports ─────────────────────────────────────────────────────────
    ("/lab-reports",                   "/lab-reports"),
    ("/lab-report",                    "/lab-reports"),
    ("/lab-report-writing",            "/lab-reports"),

    # ── Data analysis ───────────────────────────────────────────────────────
    ("/data-analysis",                 "/data-analysis"),
    ("/data-analysis-help",            "/data-analysis"),
    ("/statistical-analysis",          "/data-analysis"),
    ("/statistics-help",               "/data-analysis"),

    # ── Reflective essays ───────────────────────────────────────────────────
    ("/reflective-essays",             "/reflective-essays"),
    ("/reflective-essay",              "/reflective-essays"),
    ("/reflective-essay-writing",      "/reflective-essays"),

    # ── Presentations ───────────────────────────────────────────────────────
    ("/presentations",                 "/presentations"),
    ("/presentation-writing",          "/presentations"),
    ("/presentation-help",             "/presentations"),

    # ── Proofreading / editing ──────────────────────────────────────────────
    ("/proofreading",                  "/proofreading"),
    ("/proofreading-service",          "/proofreading"),
    ("/editing-service",               "/proofreading"),
    ("/essay-editing-service",         "/proofreading"),
    ("/editing-proofreading-service",  "/proofreading"),

    # ── Creative writing ────────────────────────────────────────────────────
    ("/creative-writing",              "/creative-writing"),
    ("/creative-writing-service",      "/creative-writing"),

    # ── Generic old top-level pages ─────────────────────────────────────────
    ("/about-us",    "/about"),
    ("/contact-us",  "/contact"),
    ("/our-writers", "/writers"),
    ("/place-order", "/order"),
    ("/order-now",   "/order"),
]


class Command(BaseCommand):
    help = "Seed Wagtail 301 redirects from old EssayManiacs flat URLs to new flat canonical paths (/:slug)"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="essaymaniacs.com")

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

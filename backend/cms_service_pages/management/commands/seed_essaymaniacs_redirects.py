"""
Management command: seed_essaymaniacs_redirects
===============================================

Creates 301 redirects in Wagtail from old flat EssayManiacs URL paths
to the new /services/<slug>/ structure.

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
    ("/essays",                        "/services/essays"),
    ("/essay-writing",                 "/services/essays"),
    ("/essay-writing-service",         "/services/essays"),
    ("/write-my-essay",                "/services/essays"),
    ("/buy-essay",                     "/services/essays"),
    ("/pay-for-essay",                 "/services/essays"),
    ("/cheap-essays",                  "/services/essays"),

    # ── Argumentative essays ────────────────────────────────────────────────
    ("/argumentative-essays",          "/services/argumentative-essays"),
    ("/argumentative-essay",           "/services/argumentative-essays"),
    ("/argumentative-essay-help",      "/services/argumentative-essays"),
    ("/write-my-argumentative-essay",  "/services/argumentative-essays"),

    # ── Research papers ─────────────────────────────────────────────────────
    ("/research-papers",               "/services/research-papers"),
    ("/research-paper",                "/services/research-papers"),
    ("/research-paper-writing",        "/services/research-papers"),
    ("/research-paper-writing-service","/services/research-papers"),
    ("/write-my-research-paper",       "/services/research-papers"),
    ("/buy-research-paper",            "/services/research-papers"),

    # ── Dissertations ───────────────────────────────────────────────────────
    ("/dissertations",                 "/services/dissertations"),
    ("/dissertation-writing",          "/services/dissertations"),
    ("/dissertation-writing-service",  "/services/dissertations"),
    ("/write-my-dissertation",         "/services/dissertations"),
    ("/thesis-writing",                "/services/dissertations"),
    ("/thesis-writing-service",        "/services/dissertations"),

    # ── Term papers ─────────────────────────────────────────────────────────
    ("/term-papers",                   "/services/term-papers"),
    ("/term-paper",                    "/services/term-papers"),
    ("/term-paper-writing",            "/services/term-papers"),
    ("/term-paper-writing-service",    "/services/term-papers"),

    # ── Case studies ────────────────────────────────────────────────────────
    ("/case-studies",                  "/services/case-studies"),
    ("/case-study",                    "/services/case-studies"),
    ("/case-study-writing",            "/services/case-studies"),
    ("/case-study-writing-service",    "/services/case-studies"),

    # ── Coursework / homework ───────────────────────────────────────────────
    ("/coursework",                    "/services/coursework"),
    ("/coursework-help",               "/services/coursework"),
    ("/coursework-writing-service",    "/services/coursework"),
    ("/do-my-coursework",              "/services/coursework"),
    ("/assignment-help",               "/services/coursework"),
    ("/homework-help",                 "/services/coursework"),

    # ── Admission / personal statements ────────────────────────────────────
    ("/admission-essays",              "/services/admission-essays"),
    ("/admission-essay",               "/services/admission-essays"),
    ("/admission-essay-writing",       "/services/admission-essays"),
    ("/college-essay-writing",         "/services/admission-essays"),
    ("/college-essay-writing-service", "/services/admission-essays"),
    ("/personal-statements",           "/services/personal-statements"),
    ("/personal-statement",            "/services/personal-statements"),
    ("/personal-statement-writing",    "/services/personal-statements"),

    # ── Scholarship essays ──────────────────────────────────────────────────
    ("/scholarship-essays",            "/services/scholarship-essays"),
    ("/scholarship-essay",             "/services/scholarship-essays"),
    ("/scholarship-essay-writing",     "/services/scholarship-essays"),

    # ── Literature reviews ──────────────────────────────────────────────────
    ("/literature-reviews",            "/services/literature-reviews"),
    ("/literature-review",             "/services/literature-reviews"),
    ("/literature-review-writing",     "/services/literature-reviews"),
    ("/literature-review-writing-service", "/services/literature-reviews"),

    # ── Annotated bibliographies ────────────────────────────────────────────
    ("/annotated-bibliographies",      "/services/annotated-bibliographies"),
    ("/annotated-bibliography",        "/services/annotated-bibliographies"),

    # ── Book reports ────────────────────────────────────────────────────────
    ("/book-reports",                  "/services/book-reports"),
    ("/book-report",                   "/services/book-reports"),
    ("/book-report-writing",           "/services/book-reports"),

    # ── Lab reports ─────────────────────────────────────────────────────────
    ("/lab-reports",                   "/services/lab-reports"),
    ("/lab-report",                    "/services/lab-reports"),
    ("/lab-report-writing",            "/services/lab-reports"),

    # ── Data analysis ───────────────────────────────────────────────────────
    ("/data-analysis",                 "/services/data-analysis"),
    ("/data-analysis-help",            "/services/data-analysis"),
    ("/statistical-analysis",          "/services/data-analysis"),
    ("/statistics-help",               "/services/data-analysis"),

    # ── Reflective essays ───────────────────────────────────────────────────
    ("/reflective-essays",             "/services/reflective-essays"),
    ("/reflective-essay",              "/services/reflective-essays"),
    ("/reflective-essay-writing",      "/services/reflective-essays"),

    # ── Presentations ───────────────────────────────────────────────────────
    ("/presentations",                 "/services/presentations"),
    ("/presentation-writing",          "/services/presentations"),
    ("/presentation-help",             "/services/presentations"),

    # ── Proofreading / editing ──────────────────────────────────────────────
    ("/proofreading",                  "/services/proofreading"),
    ("/proofreading-service",          "/services/proofreading"),
    ("/editing-service",               "/services/proofreading"),
    ("/essay-editing-service",         "/services/proofreading"),
    ("/editing-proofreading-service",  "/services/proofreading"),

    # ── Creative writing ────────────────────────────────────────────────────
    ("/creative-writing",              "/services/creative-writing"),
    ("/creative-writing-service",      "/services/creative-writing"),

    # ── Generic old top-level pages ─────────────────────────────────────────
    ("/about-us",    "/about"),
    ("/contact-us",  "/contact"),
    ("/our-writers", "/writers"),
    ("/place-order", "/order"),
    ("/order-now",   "/order"),
]


class Command(BaseCommand):
    help = "Seed Wagtail 301 redirects from old EssayManiacs flat URLs to new /services/ paths"

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

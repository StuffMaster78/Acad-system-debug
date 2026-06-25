"""
Management command: seed_nursemygrade_redirects
===============================================

Creates 301 redirects from old flat NurseMyGrade URL paths to new flat canonical URLs (/:slug).

Usage:
    python manage.py seed_nursemygrade_redirects
    python manage.py seed_nursemygrade_redirects --site nursemygrade.com
"""

from django.core.management.base import BaseCommand, CommandParser

REDIRECTS = [
    # ── Nursing essays ──────────────────────────────────────────────────────
    ("/nursing-essays",                    "/online-nursing-essays-help"),
    ("/nursing-essay",                     "/online-nursing-essays-help"),
    ("/online-nursing-essays",             "/online-nursing-essays-help"),
    ("/nursing-essay-writing",             "/online-nursing-essays-help"),
    ("/nursing-essay-writing-service",     "/online-nursing-essays-help"),
    ("/nursing-assignment-help",           "/online-nursing-essays-help"),
    ("/write-my-nursing-essay",            "/online-nursing-essays-help"),
    ("/buy-nursing-essay",                 "/online-nursing-essays-help"),

    # ── Care plans ──────────────────────────────────────────────────────────
    ("/nursing-care-plan",                 "/nursing-care-plan-writing-services"),
    ("/care-plan-writing",                 "/nursing-care-plan-writing-services"),
    ("/care-plan-help",                    "/nursing-care-plan-writing-services"),
    ("/nanda-care-plan",                   "/nursing-care-plan-writing-services"),

    # ── SOAP notes ──────────────────────────────────────────────────────────
    ("/soap-notes",                        "/nursing-soap-note-writing-help"),
    ("/soap-note",                         "/nursing-soap-note-writing-help"),
    ("/soap-note-writing",                 "/nursing-soap-note-writing-help"),
    ("/soap-note-help",                    "/nursing-soap-note-writing-help"),

    # ── Capstone projects ───────────────────────────────────────────────────
    ("/nursing-capstone",                  "/nursing-capstone-project-writing-service"),
    ("/capstone-project",                  "/nursing-capstone-project-writing-service"),
    ("/nursing-capstone-project",          "/nursing-capstone-project-writing-service"),

    # ── Research papers ─────────────────────────────────────────────────────
    ("/nursing-research-paper",            "/best-online-nursing-research-paper-service"),
    ("/nursing-research-papers",           "/best-online-nursing-research-paper-service"),
    ("/research-paper",                    "/best-online-nursing-research-paper-service"),
    ("/research-paper-writing",            "/best-online-nursing-research-paper-service"),

    # ── Case studies ────────────────────────────────────────────────────────
    ("/nursing-case-study",                "/nursing-case-study-help"),
    ("/case-study-help",                   "/nursing-case-study-help"),
    ("/case-study-writing",                "/nursing-case-study-help"),

    # ── Dissertations ───────────────────────────────────────────────────────
    ("/nursing-dissertation",              "/nursing-dissertation-writing-service"),
    ("/dissertation-writing",              "/nursing-dissertation-writing-service"),
    ("/dnp-capstone",                      "/nursing-dissertation-writing-service"),

    # ── Concept maps ────────────────────────────────────────────────────────
    ("/concept-map",                       "/concept-map-writing-services"),
    ("/nursing-concept-map",               "/concept-map-writing-services"),
    ("/mind-map",                          "/concept-map-writing-services"),

    # ── Coursework / class help ─────────────────────────────────────────────
    ("/nursing-coursework",                "/nursing-coursework-help-online"),
    ("/coursework-help",                   "/nursing-coursework-help-online"),
    ("/nursing-class-help",                "/nursing-class-help-online"),
    ("/take-my-nursing-class",             "/nursing-class-help-online"),
    ("/online-class-help",                 "/nursing-class-help-online"),

    # ── Shadow health ───────────────────────────────────────────────────────
    ("/shadow-health",                     "/shadow-health-help-online"),
    ("/shadow-health-help",                "/shadow-health-help-online"),

    # ── iHuman ─────────────────────────────────────────────────────────────
    ("/ihuman",                            "/ihuman-help"),
    ("/ihuman-help",                       "/ihuman-help"),

    # ── BSN / MSN writing ───────────────────────────────────────────────────
    ("/bsn-writing",                       "/reliable-and-cheap-bsn-writing-service"),
    ("/msn-writing",                       "/reliable-msn-writing-services"),
    ("/graduate-nursing-writing",          "/postgraduate-nursing-papers-assignments-help"),

    # ── APA format ──────────────────────────────────────────────────────────
    ("/apa-format",                        "/apa-format-nursing-paper-writing-service"),
    ("/apa-format-nursing",                "/apa-format-nursing-paper-writing-service"),

    # ── Generic old pages ───────────────────────────────────────────────────
    ("/about-us",    "/about"),
    ("/contact-us",  "/contact"),
    ("/place-order", "/order"),
    ("/order-now",   "/order"),
]


class Command(BaseCommand):
    help = "Seed Wagtail 301 redirects from old NurseMyGrade flat URLs to new flat canonical paths (/:slug)"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="nursemygrade.com")

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

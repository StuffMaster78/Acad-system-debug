"""
Management command: seed_nursemygrade_redirects
===============================================

Creates 301 redirects from old flat NurseMyGrade URL paths to new /services/ structure.

Usage:
    python manage.py seed_nursemygrade_redirects
    python manage.py seed_nursemygrade_redirects --site nursemygrade.com
"""

from django.core.management.base import BaseCommand, CommandParser

REDIRECTS = [
    # ── Nursing essays ──────────────────────────────────────────────────────
    ("/nursing-essays",                    "/services/online-nursing-essays-help"),
    ("/nursing-essay",                     "/services/online-nursing-essays-help"),
    ("/online-nursing-essays",             "/services/online-nursing-essays-help"),
    ("/nursing-essay-writing",             "/services/online-nursing-essays-help"),
    ("/nursing-essay-writing-service",     "/services/online-nursing-essays-help"),
    ("/nursing-assignment-help",           "/services/online-nursing-essays-help"),
    ("/write-my-nursing-essay",            "/services/online-nursing-essays-help"),
    ("/buy-nursing-essay",                 "/services/online-nursing-essays-help"),

    # ── Care plans ──────────────────────────────────────────────────────────
    ("/nursing-care-plan",                 "/services/nursing-care-plan-writing-services"),
    ("/care-plan-writing",                 "/services/nursing-care-plan-writing-services"),
    ("/care-plan-help",                    "/services/nursing-care-plan-writing-services"),
    ("/nanda-care-plan",                   "/services/nursing-care-plan-writing-services"),

    # ── SOAP notes ──────────────────────────────────────────────────────────
    ("/soap-notes",                        "/services/nursing-soap-note-writing-help"),
    ("/soap-note",                         "/services/nursing-soap-note-writing-help"),
    ("/soap-note-writing",                 "/services/nursing-soap-note-writing-help"),
    ("/soap-note-help",                    "/services/nursing-soap-note-writing-help"),

    # ── Capstone projects ───────────────────────────────────────────────────
    ("/nursing-capstone",                  "/services/nursing-capstone-project-writing-service"),
    ("/capstone-project",                  "/services/nursing-capstone-project-writing-service"),
    ("/nursing-capstone-project",          "/services/nursing-capstone-project-writing-service"),

    # ── Research papers ─────────────────────────────────────────────────────
    ("/nursing-research-paper",            "/services/best-online-nursing-research-paper-service"),
    ("/nursing-research-papers",           "/services/best-online-nursing-research-paper-service"),
    ("/research-paper",                    "/services/best-online-nursing-research-paper-service"),
    ("/research-paper-writing",            "/services/best-online-nursing-research-paper-service"),

    # ── Case studies ────────────────────────────────────────────────────────
    ("/nursing-case-study",                "/services/nursing-case-study-help"),
    ("/case-study-help",                   "/services/nursing-case-study-help"),
    ("/case-study-writing",                "/services/nursing-case-study-help"),

    # ── Dissertations ───────────────────────────────────────────────────────
    ("/nursing-dissertation",              "/services/nursing-dissertation-writing-service"),
    ("/dissertation-writing",              "/services/nursing-dissertation-writing-service"),
    ("/dnp-capstone",                      "/services/nursing-dissertation-writing-service"),

    # ── Concept maps ────────────────────────────────────────────────────────
    ("/concept-map",                       "/services/concept-map-writing-services"),
    ("/nursing-concept-map",               "/services/concept-map-writing-services"),
    ("/mind-map",                          "/services/concept-map-writing-services"),

    # ── Coursework / class help ─────────────────────────────────────────────
    ("/nursing-coursework",                "/services/nursing-coursework-help-online"),
    ("/coursework-help",                   "/services/nursing-coursework-help-online"),
    ("/nursing-class-help",                "/services/nursing-class-help-online"),
    ("/take-my-nursing-class",             "/services/nursing-class-help-online"),
    ("/online-class-help",                 "/services/nursing-class-help-online"),

    # ── Shadow health ───────────────────────────────────────────────────────
    ("/shadow-health",                     "/services/shadow-health-help-online"),
    ("/shadow-health-help",                "/services/shadow-health-help-online"),

    # ── iHuman ─────────────────────────────────────────────────────────────
    ("/ihuman",                            "/services/ihuman-help"),
    ("/ihuman-help",                       "/services/ihuman-help"),

    # ── BSN / MSN writing ───────────────────────────────────────────────────
    ("/bsn-writing",                       "/services/reliable-and-cheap-bsn-writing-service"),
    ("/msn-writing",                       "/services/reliable-msn-writing-services"),
    ("/graduate-nursing-writing",          "/services/postgraduate-nursing-papers-assignments-help"),

    # ── APA format ──────────────────────────────────────────────────────────
    ("/apa-format",                        "/services/apa-format-nursing-paper-writing-service"),
    ("/apa-format-nursing",                "/services/apa-format-nursing-paper-writing-service"),

    # ── Generic old pages ───────────────────────────────────────────────────
    ("/about-us",    "/about"),
    ("/contact-us",  "/contact"),
    ("/place-order", "/order"),
    ("/order-now",   "/order"),
]


class Command(BaseCommand):
    help = "Seed Wagtail 301 redirects from old NurseMyGrade flat URLs to new /services/ paths"

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

"""
Management command: seed_gradecrest_redirects
===============================================

Creates 301 redirects in Wagtail from the old gradecrest.com URL structure
to flat canonical URLs (/:slug).

Old URLs (top-level, no /services/ prefix, different slugs):
    /write-my-essay  →  /services/essay-writing
    /research-paper  →  /services/research-papers
    etc.

Idempotent — skips redirects that already exist.

Usage:
    python manage.py seed_gradecrest_redirects
    python manage.py seed_gradecrest_redirects --site gradecrest.com
"""

from django.core.management.base import BaseCommand, CommandParser

# Map of old path → new path.
# Add any additional old URLs from the live gradecrest.com here.
REDIRECTS = [
    # Core service pages — common keyword-slug patterns from old site
    ("/write-my-essay", "/essay-writing"),
    ("/essay-writing-service", "/essay-writing"),
    ("/buy-essay", "/essay-writing"),
    ("/pay-for-essay", "/essay-writing"),
    ("/research-paper-writing", "/research-papers"),
    ("/research-paper-writing-service", "/research-papers"),
    ("/write-my-research-paper", "/research-papers"),
    ("/dissertation-writing", "/dissertations"),
    ("/dissertation-writing-service", "/dissertations"),
    ("/write-my-dissertation", "/dissertations"),
    ("/nursing-essay-writing", "/nursing-essays"),
    ("/nursing-assignment-help", "/nursing-essays"),
    ("/nursing-essay-writing-service", "/nursing-essays"),
    ("/editing-proofreading-service", "/editing-proofreading"),
    ("/proofreading-service", "/editing-proofreading"),
    ("/essay-editing-service", "/editing-proofreading"),
    ("/admission-essay-writing", "/admission-essays"),
    ("/personal-statement-writing", "/admission-essays"),
    ("/college-essay-writing-service", "/admission-essays"),
    ("/term-paper-writing", "/term-papers"),
    ("/term-paper-writing-service", "/term-papers"),
    ("/write-my-term-paper", "/term-papers"),
    ("/case-study-writing", "/case-studies"),
    ("/case-study-writing-service", "/case-studies"),
    ("/coursework-help", "/coursework"),
    ("/coursework-writing-service", "/coursework"),
    ("/do-my-coursework", "/coursework"),
    ("/literature-review-writing", "/literature-review"),
    ("/literature-review-writing-service", "/literature-review"),
    ("/thesis-writing-service", "/thesis-writing"),
    ("/write-my-thesis", "/thesis-writing"),
    ("/data-analysis-help", "/data-analysis"),
    ("/statistical-analysis-service", "/data-analysis"),
    ("/online-class-help", "/online-class-help"),
    ("/take-my-online-class", "/online-class-help"),
    ("/homework-help", "/homework-help"),
    ("/do-my-homework", "/homework-help"),
    # Generic old top-level pages that may have existed
    ("/services", "/services"),  # no redirect needed — same URL
    ("/about-us", "/about"),
    ("/contact-us", "/contact"),
    ("/how-it-works", "/how-it-works"),
    ("/reviews", "/reviews"),
    ("/pricing", "/pricing"),
    ("/blog", "/blog"),
]


class Command(BaseCommand):
    help = "Seed Wagtail redirects from old gradecrest.com URL structure to new flat canonical paths (/:slug)"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="gradecrest.com")

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
            # Skip same-URL entries
            if old_path == new_path:
                skipped += 1
                continue

            # Wagtail Redirect stores old_path without trailing slash
            old_path_normalised = old_path.rstrip("/")

            if Redirect.objects.filter(site=site, old_path=old_path_normalised).exists():
                self.stdout.write(f"  EXISTS  {old_path}")
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
        self.stdout.write(self.style.SUCCESS(f"Done — {created} redirects created, {skipped} skipped"))
        self.stdout.write(
            "Note: Add any additional old URLs from your live site analytics before going live."
        )

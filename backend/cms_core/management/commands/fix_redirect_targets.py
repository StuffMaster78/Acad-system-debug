"""
Fix Wagtail redirect records whose targets still use /blog/ or /services/ prefixes.

Converts:
  /blog/<slug>      →  /<slug>
  /services/<slug>  →  /<slug>

Run with --dry-run first to preview.

Usage:
    python manage.py fix_redirect_targets --dry-run
    python manage.py fix_redirect_targets
    python manage.py fix_redirect_targets --site gradecrest.com
"""

import re

from django.core.management.base import BaseCommand

_PREFIXED = re.compile(r"^/(blog|services)/([\w-]+)/?$")


class Command(BaseCommand):
    help = "Flatten /blog/<slug> and /services/<slug> redirect targets to /<slug>"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--site", default=None, help="Restrict to one site hostname")

    def handle(self, *args, **options):
        from wagtail.contrib.redirects.models import Redirect

        dry = options["dry_run"]
        site_filter = options.get("site")

        qs = Redirect.objects.all()
        if site_filter:
            from wagtail.models import Site
            try:
                site = Site.objects.get(hostname=site_filter)
                qs = qs.filter(site=site)
            except Site.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"No site for '{site_filter}'."))
                return

        fixed = 0
        for redirect in qs.iterator():
            m = _PREFIXED.match(redirect.redirect_link or "")
            if not m:
                continue
            new_target = f"/{m.group(2)}"
            label = f"{redirect.old_path}  →  {redirect.redirect_link}"
            if dry:
                self.stdout.write(f"  [dry] {label}  →  {new_target}")
            else:
                redirect.redirect_link = new_target
                redirect.save(update_fields=["redirect_link"])
                self.stdout.write(self.style.SUCCESS(f"  fixed  {label}  →  {new_target}"))
            fixed += 1

        verb = "Would fix" if dry else "Fixed"
        self.stdout.write(self.style.SUCCESS(f"\n{verb}: {fixed} redirect(s)"))
        if dry:
            self.stdout.write("Run without --dry-run to apply.")

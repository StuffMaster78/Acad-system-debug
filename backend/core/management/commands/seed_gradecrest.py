"""
Management command to seed gradecrest.com as a client portal tenant.

Run once per environment:
    python manage.py seed_gradecrest
    python manage.py seed_gradecrest --domain https://gradecrest.com
    python manage.py seed_gradecrest --domain http://localhost:5174  # dev

This is safe to re-run — all creates use update_or_create.

What it seeds:
  1. Website          gradecrest.com (or --domain)
  2. WebsiteBranding  brand identity + payment disclosure
  3. PortalDefinition client_portal (ensures it exists; does not change its domain
                      — the middleware resolves app.gradecrest.com via parent-domain
                      fallback so no explicit portal domain mapping is needed)
"""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed gradecrest.com Website, WebsiteBranding, and client PortalDefinition."

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            default="https://gradecrest.com",
            help="Marketing domain for the website record (default: https://gradecrest.com)",
        )
        parser.add_argument(
            "--app-domain",
            default="https://app.gradecrest.com",
            help="Portal SPA subdomain — used only in CORS reminder output (default: https://app.gradecrest.com)",
        )

    def handle(self, *args, **options):
        domain     = options["domain"].rstrip("/")
        app_domain = options["app_domain"].rstrip("/")

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\nSeeding GradeCrest tenant ({domain})\n"
        ))

        website = self._seed_website(domain)
        self._seed_branding(website)
        self._seed_portal()

        from django.core import management as mgmt

        # ── Academic settings & pricing rates ─────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n⚙️  Seeding academic settings…\n"))
        mgmt.call_command("populate_academic_settings", domain)
        self.stdout.write(self.style.MIGRATE_HEADING("\n⚙️  Seeding pricing defaults…\n"))
        mgmt.call_command("seed_pricing_defaults", domain)

        # ── Wagtail blog + service pages (needs setup_tenants first) ──────
        for cmd in ("seed_gradecrest_blog", "seed_gradecrest_services", "seed_gradecrest_redirects"):
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n📄  Running {cmd}…\n"))
            try:
                mgmt.call_command(cmd)
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f" ⚠️  {cmd} skipped — run setup_tenants first ({exc})\n"))

        # ── Announcement bar ──────────────────────────────────────────────
        self._seed_promo_bar(domain, code="GRADE15", message="Get 10% off your first order", suffix="Use code GRADE15")

        self._seed_cors_reminder(domain, app_domain)
        self.stdout.write(self.style.SUCCESS("\nDone. GradeCrest tenant is ready.\n"))

    # ----------------------------------------------------------------
    # Internal seeders
    # ----------------------------------------------------------------

    def _seed_website(self, domain: str):
        from websites.models.websites import Website

        website, created = Website.objects.update_or_create(
            domain=domain,
            defaults={
                "name": "GradeCrest",
                "slug": "gradecrest",
                "is_active": True,
                "contact_email": "support@gradecrest.com",
            },
        )
        self._log("Website", website.name, created)
        return website

    def _seed_branding(self, website):
        from websites.models.website_branding import WebsiteBranding

        branding, created = WebsiteBranding.objects.update_or_create(
            website=website,
            defaults={
                "brand_name": "GradeCrest",
                "tagline": "Expert academic writing by verified human specialists.",
                "homepage_headline": "Academic Writing Help from Real Experts",
                "homepage_subheadline": (
                    "Human-written papers from $13/page — essays, dissertations, "
                    "research papers, and more across 100+ subjects."
                ),
                "primary_color": "#0e7a61",     # gc-600 (brand green)
                "secondary_color": "#0f172a",   # navy-900
                "accent_color": "#0d9488",      # teal-600
                "payment_processor_name": "OrderBridge Payments",
                "payment_statement_descriptor": "ORDERBRIDGE PAYMENTS",
                "payment_client_disclosure_text": (
                    "Your payment is securely processed by OrderBridge Payments, "
                    "our authorised billing partner. Your bank or card statement may "
                    "show 'ORDERBRIDGE PAYMENTS'."
                ),
                "payment_requires_acknowledgement": True,
                "is_public": True,
            },
        )
        self._log("WebsiteBranding", branding.brand_name, created)
        return branding

    def _seed_portal(self):
        """
        Ensure the global client_portal PortalDefinition exists.

        We deliberately do NOT update its domain — app.gradecrest.com is
        resolved to the GradeCrest website via the middleware's parent-domain
        fallback (app.gradecrest.com → gradecrest.com), so no explicit portal
        domain entry is required for branding to work.
        """
        from accounts.models.portal_definition import PortalDefinition

        portal, created = PortalDefinition.objects.get_or_create(
            code="client_portal",
            defaults={
                "name": "Client Portal",
                "domain": "localhost",
                "is_active": True,
            },
        )
        self._log("PortalDefinition (client_portal)", portal.domain, created)

    def _seed_promo_bar(self, domain: str, *, code: str, message: str, suffix: str):
        bare = domain.replace("https://", "").replace("http://", "").split(":")[0]
        try:
            from wagtail.models import Site
            from cms_core.models import TenantSEOSettings
            site = Site.objects.filter(hostname=bare).first()
            if not site:
                self.stdout.write(self.style.WARNING(f" ⚠️  Promo bar skipped — no Wagtail Site for {bare} (run setup_tenants first)\n"))
                return
            settings = TenantSEOSettings.for_site(site)
            settings.promo_bar_enabled = True
            settings.promo_code        = code
            settings.promo_message     = message
            settings.promo_suffix      = suffix
            settings.save()
            self.stdout.write(f"  Updated  TenantSEOSettings (promo bar): {code}")
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f" ⚠️  Promo bar skipped: {exc}\n"))

    def _seed_cors_reminder(self, domain: str, app_domain: str):
        bare     = domain.replace("https://", "").replace("http://", "")
        app_bare = app_domain.replace("https://", "").replace("http://", "")
        self.stdout.write(
            self.style.WARNING(
                f"\nAdd these to your production .env:\n\n"
                f"  ALLOWED_HOSTS=...,{bare},{app_bare}\n"
                f"  CORS_ALLOWED_ORIGINS=...,{domain},{app_domain}\n"
                f"  CSRF_TRUSTED_ORIGINS=...,{domain},{app_domain}\n"
            )
        )

    def _log(self, model: str, identifier: str, created: bool):
        verb = "Created" if created else "Updated"
        self.stdout.write(f"  {verb:8s} {model}: {identifier}")

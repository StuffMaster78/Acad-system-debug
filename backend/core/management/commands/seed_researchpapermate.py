"""
Management command to seed researchpapermate.com as a client portal tenant.

Run once per environment:
    python manage.py seed_researchpapermate
    python manage.py seed_researchpapermate --domain https://researchpapermate.com
    python manage.py seed_researchpapermate --domain http://localhost:3000  # dev

This is safe to re-run — all creates use update_or_create.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed researchpapermate.com Website, WebsiteBranding, and client PortalDefinition."

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            default="https://researchpapermate.com",
            help="Primary domain for the website record (default: https://researchpapermate.com)",
        )
        parser.add_argument(
            "--app-domain",
            default="https://app.researchpapermate.com",
            help="Dashboard subdomain for the client portal (default: https://app.researchpapermate.com)",
        )

    def handle(self, *args, **options):
        domain = options["domain"].rstrip("/")
        app_domain = options["app_domain"].rstrip("/")

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n🔧  Seeding ResearchPaperMate tenant ({domain})\n"
        ))

        website  = self._seed_website(domain)
        branding = self._seed_branding(website)
        self._seed_portal()

        from django.core import management as mgmt

        # ── Academic settings & pricing rates ─────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n⚙️  Seeding academic settings…\n"))
        mgmt.call_command("populate_academic_settings", domain)
        self.stdout.write(self.style.MIGRATE_HEADING("\n⚙️  Seeding pricing defaults…\n"))
        mgmt.call_command("seed_pricing_defaults", domain)

        # ── Wagtail blog content (needs setup_tenants first) ──────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n📄  Seeding blog content…\n"))
        try:
            mgmt.call_command("seed_researchpapermate_blog")
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f" ⚠️  Blog seed skipped — run setup_tenants first ({exc})\n"))

        # ── Announcement bar ──────────────────────────────────────────────
        self._seed_promo_bar(domain, code="PAPER15", message="Get 10% off your first order", suffix="Use code PAPER15")

        self._seed_cors_reminder(domain, app_domain)
        self.stdout.write(self.style.SUCCESS("\n✅  Done. ResearchPaperMate tenant is ready.\n"))

    # ----------------------------------------------------------------
    # Internal seeders
    # ----------------------------------------------------------------

    def _seed_website(self, domain: str):
        from websites.models.websites import Website

        website, created = Website.objects.update_or_create(
            domain=domain,
            defaults={
                "name": "ResearchPaperMate",
                "slug": "researchpapermate",
                "is_active": True,
                "contact_email": "support@researchpapermate.com",
            },
        )
        self._log("Website", website.name, created)
        return website

    def _seed_branding(self, website):
        from websites.models.website_branding import WebsiteBranding

        branding, created = WebsiteBranding.objects.update_or_create(
            website=website,
            defaults={
                "brand_name": "ResearchPaperMate",
                "tagline": "Reliable academic writing by humans, from $15/page.",
                "homepage_headline": "Get Research Papers, Essays & Assignments Done!",
                "homepage_subheadline": (
                    "Reliable research paper writing service from $15/page — "
                    "written by human experts across 100+ subjects."
                ),
                "primary_color": "#163e88",
                "secondary_color": "#0d2455",
                "accent_color": "#14b8a6",
                # Payment disclosure — update processor_name once Stripe is live
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
        from accounts.models.portal_definition import PortalDefinition

        # Ensure the global client_portal exists. We deliberately do NOT update
        # its domain — app.* subdomains resolve to their tenant website via the
        # middleware's parent-domain fallback, so no per-tenant domain entry is
        # needed. Overwriting the domain here would break other client tenants.
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
            self._log("TenantSEOSettings (promo bar)", f"{code} — {message}", False)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f" ⚠️  Promo bar skipped: {exc}\n"))

    def _seed_cors_reminder(self, domain: str, app_domain: str):
        bare = domain.replace("https://", "").replace("http://", "")
        app_bare = app_domain.replace("https://", "").replace("http://", "")
        self.stdout.write(
            self.style.WARNING(
                f"\n⚠️  Add these to your production .env:\n\n"
                f"  ALLOWED_HOSTS=...,{bare},{app_bare}\n"
                f"  CORS_ALLOWED_ORIGINS=...,{domain},{app_domain}\n"
                f"  CSRF_TRUSTED_ORIGINS=...,{domain},{app_domain}\n"
            )
        )

    def _log(self, model: str, identifier: str, created: bool):
        verb = "Created" if created else "Updated"
        self.stdout.write(f"  {verb:8s} {model}: {identifier}")
